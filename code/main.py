"""
鼓譜語音講解產生器
用法：python code/main.py --input ./input/Sugar.pdf --output ./output/
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pdf2image import convert_from_path


def pdf_to_images(pdf_path: Path, output_dir: Path, dpi: int = 200) -> list[Path]:
    """將 PDF 轉換為 PNG 圖片"""
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    pages = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []

    for i, page in enumerate(pages, start=1):
        image_path = images_dir / f"page_{i}.png"
        page.save(image_path, "PNG")
        image_paths.append(image_path)
        print(f"  已轉換：{image_path.name}")

    return image_paths


def load_prompt() -> str:
    """讀取樂譜解析 prompt"""
    prompt_path = Path(__file__).parent / "parse_drum_sheet_prompt.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_drum_sheet(image_paths: list[Path], output_dir: Path, model: str = "gemini-2.5-flash") -> dict:
    """使用 Gemini Vision API 解析鼓譜圖片"""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = load_prompt()

    # 準備圖片內容
    contents = [prompt]
    for image_path in image_paths:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))

    # 呼叫 Gemini Vision API（強制 JSON 輸出）
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
    )

    output_text = response.text

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as e:
        # 儲存原始回應以便 debug
        debug_path = output_dir / "debug_response.txt"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"  原始回應已儲存至 {debug_path}")
        raise e


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="鼓譜語音講解產生器")
    parser.add_argument("--input", required=True, help="PDF 樂譜路徑")
    parser.add_argument("--output", default="./output", help="輸出資料夾")
    args = parser.parse_args()

    pdf_path = Path(args.input)
    if not pdf_path.exists():
        print(f"錯誤：找不到檔案 {pdf_path}")
        return

    # 建立輸出資料夾：{樂譜名}_{YYYYMMDD_HHMM}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    song_name = pdf_path.stem
    output_dir = Path(args.output) / f"{song_name}_{timestamp}"

    print(f"處理樂譜：{pdf_path.name}")
    print(f"輸出位置：{output_dir}")

    # 步驟 1：PDF 轉圖片
    print("\n[步驟 1] PDF 轉圖片...")
    image_paths = pdf_to_images(pdf_path, output_dir)
    print(f"完成，共 {len(image_paths)} 頁")

    # 步驟 2：Gemini Vision API 解析樂譜
    print("\n[步驟 2] Gemini Vision API 解析樂譜...")
    try:
        parsed_data = parse_drum_sheet(image_paths, output_dir)
        
        # 儲存 JSON
        json_path = output_dir / f"{song_name}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        print(f"完成，已儲存至 {json_path.name}")
    except Exception as e:
        print(f"解析失敗：{e}")
        return


if __name__ == "__main__":
    main()
