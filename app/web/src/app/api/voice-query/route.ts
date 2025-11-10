import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const audioBlob = formData.get('audio');
    const language = formData.get('language') || 'en';

    if (!audioBlob) {
      return NextResponse.json(
        { error: 'No audio file provided' },
        { status: 400 }
      );
    }

    // Forward to backend FastAPI server
    const backendFormData = new FormData();
    backendFormData.append('audio', audioBlob);
    backendFormData.append('language', language as string);

    const response = await fetch(`${BACKEND_URL}/stt`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Voice processing failed' },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    // Now search with the transcribed text
    const searchResponse = await fetch(`${BACKEND_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: data.text,
        language: language,
        limit: 20,
      }),
    });

    if (!searchResponse.ok) {
      const error = await searchResponse.json();
      return NextResponse.json(
        { error: error.detail || 'Search failed' },
        { status: searchResponse.status }
      );
    }

    const searchData = await searchResponse.json();

    return NextResponse.json({
      transcript: data.text,
      language: data.language,
      recipes: searchData.recipes,
      total: searchData.total,
      processingTime: data.processing_time + searchData.processing_time,
    });
  } catch (error) {
    console.error('Voice query error:', error);
    return NextResponse.json(
      { error: 'Internal server error processing voice query' },
      { status: 500 }
    );
  }
}
