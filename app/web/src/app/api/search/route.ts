import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { query, language = 'en', limit = 20, filters } = body;

    if (!query) {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    // Format request according to FastAPI SearchRequest model
    const searchRequest = {
      query: {
        text: query,
        lang: language,
        constraints: filters || null
      }
    };

    console.log('Sending to backend:', searchRequest);

    // Forward to backend FastAPI server
    const response = await fetch(`${BACKEND_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Backend error:', error);
      return NextResponse.json(
        { error: error.detail || 'Search failed' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend response:', data);
    
    // Map FastAPI response (results) to frontend format (recipes)
    const mappedResponse = {
      recipes: data.results || [],
      total: data.count || 0,
      query: data.query,
      translatedQuery: data.translatedQuery,
      processing_time: data.durationMs
    };
    
    return NextResponse.json(mappedResponse);
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json(
      { error: 'Internal server error during search' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const query = searchParams.get('q');
    const language = searchParams.get('lang') || 'en';
    const limit = parseInt(searchParams.get('limit') || '20');

    if (!query) {
      return NextResponse.json(
        { error: 'Query parameter "q" is required' },
        { status: 400 }
      );
    }

    // Format request according to FastAPI SearchRequest model
    const searchRequest = {
      query: {
        text: query,
        lang: language
      }
    };

    // Forward to backend FastAPI server
    const response = await fetch(`${BACKEND_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(searchRequest),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Backend error:', error);
      return NextResponse.json(
        { error: error.detail || 'Search failed' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Backend response (GET):', data);
    
    // Map FastAPI response (results) to frontend format (recipes)
    const mappedResponse = {
      recipes: data.results || [],
      total: data.count || 0,
      query: data.query,
      translatedQuery: data.translatedQuery,
      processing_time: data.durationMs
    };
    
    return NextResponse.json(mappedResponse);
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json(
      { error: 'Internal server error during search' },
      { status: 500 }
    );
  }
}
