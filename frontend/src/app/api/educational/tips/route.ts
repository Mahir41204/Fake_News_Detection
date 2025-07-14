import { NextResponse } from 'next/server';

export async function GET() {
  const educationalTips = {
    "tips": [
      "Check multiple sources before believing a claim",
      "Look for primary sources and original research",
      "Be skeptical of claims that seem too good or bad to be true",
      "Check the date of the information - old news can be misleading",
      "Look for expert consensus on scientific topics",
      "Be aware of your own biases and confirmation bias",
      "Check if the source has a history of accuracy",
      "Look for fact-checking organizations' verdicts",
      "Be cautious of emotional language and urgency",
      "Question claims that contradict established facts"
    ],
    "red_flags": [
      "Excessive emotional language",
      "Claims that seem too certain",
      "Urgency or exclusivity claims",
      "Conspiracy language patterns",
      "Lack of specific details or sources",
      "Claims that appeal to authority without evidence",
      "Information that confirms your existing beliefs too perfectly"
    ],
    "reliable_sources": [
      "Reuters", "Associated Press", "BBC", "NPR", "PBS",
      "FactCheck.org", "Snopes", "PolitiFact", "AP Fact Check"
    ]
  };

  return NextResponse.json(educationalTips);
} 