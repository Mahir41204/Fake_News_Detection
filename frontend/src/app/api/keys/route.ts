import { NextRequest, NextResponse } from "next/server";

export async function GET() {
  const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
  const response = await fetch(`${backendUrl}/api/keys`);
  const data = await response.json();
  return NextResponse.json(data);
} 