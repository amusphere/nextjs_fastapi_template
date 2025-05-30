"use server";

import { apiPost, createApiResponse } from '@/utils/api';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt } = body;

    if (!prompt) {
      return NextResponse.json(
        { error: 'プロンプトが必要です' },
        { status: 400 }
      );
    }

    // バックエンドのAIエンドポイントにapiPostを使ってリクエストを送信
    const apiResponse = await apiPost('/ai/process', { prompt });

    // apiResponseを使ってNextResponseを生成
    return createApiResponse(apiResponse);

  } catch (error) {
    console.error('AI API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '内部サーバーエラー'
      },
      { status: 500 }
    );
  }
}
