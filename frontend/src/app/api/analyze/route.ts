import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { source_text, source_url } = body;

    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";

    const response = await fetch(`${backendUrl}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: req.headers.get("Authorization") || "",
      },
      body: JSON.stringify({ source_text, source_url }),
    });

    const text = await response.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }

    if (!response.ok) {
      return NextResponse.json(
        {
          error: `Backend error: ${data.detail || response.statusText}`,
          backendStatus: response.status,
          backendResponse: data,
        },
        { status: response.status }
      );
    }

    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Proxy error:", error);
    return NextResponse.json(
      { error: `Failed to connect to the backend: ${error.message}` },
      { status: 500 }
    );
  }
} 