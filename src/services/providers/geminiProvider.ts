import { GoogleGenAI } from "@google/genai";
import dotenv, { config } from 'dotenv';
dotenv.config();

import { INCOME_CATEGORIES, SAVINGS_CATEGORIES, INVESTING_CATERGORIES, BILLS_CATEGORIES, EXPENSE_CATEGORIES } from "../../config/categories";
import type { TransactionType, TransactionData, AIProvider } from "../aiService";

const apiKey = process.env.GEMINI_API_KEY
console.log('API Key:', process.env.GEMINI_API_KEY ? 'Found' : 'Not found');
console.log('First 10 chars:', process.env.GEMINI_API_KEY?.substring(0, 10));
if (!apiKey) {
  throw new Error('GEMINI_API_KEY environment variable is required');
}

async function categorizeTransaction(rawText:string): Promise<{
  type: TransactionType;
  data: TransactionData;
  confidence: number;
}> {
  const ai = new GoogleGenAI({apiKey: apiKey!}); 
  const config = {
    temperature: 0.1, // Low temperature for consistent categorization
    maxOutputTokens: 500,
  };
  const model = 'gemini-2.0-flash-lite';
  const prompt = buildPrompt(rawText);

  const contents = [
    {
      role: 'user',
      parts: [
        {
          text: prompt
        },
      ],
    },
  ];

  const response = await ai.models.generateContent({
    model, 
    config, 
    contents,
  });

  console.log('Raw AI Response:');
  console.log('------------------------');
  console.log(response.text);
  console.log('------------------------');

  try {
    let responseText = response.text || '{}'
    if (response.text?.includes('```json')) {
    responseText = responseText.replace(/```json\s*/, '').replace(/\s*```/, '');
    }
    const result = JSON.parse(responseText);
    return validateResponse(result); // the type, data, and confidence
  } catch (error) {
    throw new Error(`Failed to parse AI response: ${error}`);
  }
}

// prompt for LLM, return a string
function buildPrompt(rawText: string): string {
    // join the array for AI readability
    return `You are a finanical transaction categorizer. Analyze this transaction text: "${rawText}"
    
    Determine both the transaction type and category from these options:
    - Income: ${INCOME_CATEGORIES.join(', ')} 
    - Savings: ${SAVINGS_CATEGORIES.join(', ')}
    - Investing: ${INVESTING_CATERGORIES.join(', ')}
    - Bills: ${BILLS_CATEGORIES.join(', ')}
    - Expense: ${EXPENSE_CATEGORIES.join(', ')}
    
    Extract the amount and create a description with the following valid JSON format only:

    {
      "type": "income|"savings"|"investing"|"bills"|"expense",
      "description" : "clean, concise description",
      "amount": number,
      "category": "exact category from the list above",
      "confidence": number between 0 and 1
    }

    Examples: 
    - "mcdonalds, 12" → {"type": "expense", "description": "McDonald's", "amount": 12, "category": "Eating Out", "confidence": 0.95}
    - "wealthfront, 500" → {"type": "savings", "description": "Savings deposit", "amount": 500, "category": "Wealthfront", "confidence": 0.90}
    - "gym membership 25" → {"type": "bills", "description": "Gym membership", "amount": 25, "category": "Gym", "confidence": 0.96}
    - "golf 33" → {"type": "expense", "description": "Golf", "amount": 33, "category": "Activity", "confidence": 0.97}
  `
}

function validateResponse(result: any): {
  type: TransactionType;
  data: TransactionData;
  confidence: number;
} {
  if (!result.type || !result.description || !result.amount || !result.category || result.confidence === undefined) {
    throw new Error('AI provided invalid response format');
  }

  if (!['income', 'savings', 'investing', 'bills', 'expense'].includes(result.type)) {
    throw new Error(`Invalid transaction type: ${result.type}`);
  }

  return {
    type: result.type,
    data: {
      description: result.description,
      amount: result.amount,
      category: result.category,
      confidence: result.confidence
    },
    confidence: result.confidence
  }
}

async function main() {
  try {
    const result = await categorizeTransaction("perfume, 100");
    console.log('Result:', result);
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
