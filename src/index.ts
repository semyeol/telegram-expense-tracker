import express from "express";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import twilio from "twilio";
//import { generateResponse } from "./controllers";

dotenv.config();

const app = express();
const port = process.env.PORT;
app.use(bodyParser.json());

//app.post("/generate", generateResponse);

app.get("/", (req, res) => {
  res.send("Hello World!");
});

const twilioClient = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

async function sendMessage() {
  const message = await twilioClient.messages.create({
    body: 'hi',
    from: process.env.TWILIO_NUMBER!,
    to: process.env.MY_NUMBER!,
  })
  console.log(message)
}

app.post("/sms", (req, res) => {
  const incomingMsg = req.body.Body;
  const sender = req.body.From;
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

sendMessage()