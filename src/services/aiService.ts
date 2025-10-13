export type TransactionType = 'income' | 'savings' | 'investing' | 'bills' | 'expense';

// interface for api shape validation
export interface TransactionData {
    description: string;
    amount: number;
    category: string;
    confidence: number;
}

export interface AIProvider {
    categorizeTransaction(rawText:string): Promise<{
        type: TransactionType;
        data: TransactionData;
        confidence: number;
    }>;
}

