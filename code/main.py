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


# 口訣對照表
INSTRUMENT_TO_SYLLABLE = {
    "kick": "懂",
    "snare": "搭",
    "hihat": "刺",
    "crash": "框",
    "tom1": "Tom1",
    "tom2": "Tom2",
    "tom3": "Tom3",
}

# 4/4 拍：4 拍，每拍有 2 個 8 分音符位置
BEATS_4_4 = [
    ("1", "1+"),   # 第 1 拍
    ("2", "2+"),   # 第 2 拍
    ("3", "3+"),   # 第 3 拍
    ("4", "4+"),   # 第 4 拍
]


def position_to_syllable(instruments: list[str]) -> str:
    """將單一位置的樂器轉成口訣"""
    if not instruments:
        return ""
    
    # 按固定順序：crash > kick > snare > hihat > tom
    syllables = []
    for inst in ["crash", "kick", "snare", "hihat", "tom1", "tom2", "tom3"]:
        if inst in instruments:
            syllables.append(INSTRUMENT_TO_SYLLABLE[inst])
    
    return "".join(syllables)


def events_to_syllables(events: list[dict], has_hihat: bool = False) -> str:
    """將 events 轉換成口訣字串（以拍為單位）"""
    if not events:
        return "休息"
    
    # 建立 position -> instruments 的對照
    pos_map = {}
    for event in events:
        pos = event.get("position", "")
        instruments = event.get("instruments", [])
        pos_map[pos] = instruments
    
    beat_syllables = []
    for pos1, pos2 in BEATS_4_4:
        # 每拍合併兩個位置的音
        inst1 = pos_map.get(pos1, [])
        inst2 = pos_map.get(pos2, [])
        
        syl1 = position_to_syllable(inst1)
        syl2 = position_to_syllable(inst2)
        
        # 合併這一拍的口訣
        beat = syl1 + syl2
        
        if beat:
            beat_syllables.append(beat)
        else:
            beat_syllables.append("嗯")  # 空拍
    
    if not any(s != "嗯" for s in beat_syllables):
        return "休息"
    
    return "、".join(beat_syllables)


def detect_difficulty(measure: dict) -> list[str]:
    """偵測小節難點"""
    difficulties = []
    events = measure.get("events", [])
    
    if not events:
        return difficulties
    
    # 1. Crash 起手：第一拍有 crash
    first_beat_instruments = []
    for event in events:
        if event.get("position") == "1":
            first_beat_instruments = event.get("instruments", [])
            break
    if "crash" in first_beat_instruments:
        difficulties.append("Crash 起手")
    
    # 2. 過門：有 tom
    has_tom = False
    for event in events:
        instruments = event.get("instruments", [])
        if any(inst in instruments for inst in ["tom1", "tom2", "tom3"]):
            has_tom = True
            break
    if has_tom:
        difficulties.append("過門")
    
    # 3. 切分：有 16 分音符位置（包含 ++）
    for event in events:
        pos = event.get("position", "")
        if "++" in pos:
            difficulties.append("切分")
            break
    
    return difficulties


def generate_transcript(parsed_data: dict) -> str:
    """將 JSON 轉換成講解逐字稿（口語化，給 TTS 朗讀）"""
    lines_output = []
    
    # 歌曲資訊
    song_info = parsed_data.get("song_info", {})
    title = song_info.get("title", "未知曲目")
    tempo = song_info.get("tempo", "?")
    
    lines_output.append(f"{title} 講解稿")
    lines_output.append(f"速度是 {tempo}")
    lines_output.append("")
    
    # 逐行處理
    for line in parsed_data.get("lines", []):
        line_number = line.get("line_number", "?")
        section_marker = line.get("section_marker", "")
        measures = line.get("measures", [])
        
        # 行標題（口語化）
        section_text = f"，{section_marker}段" if section_marker else ""
        lines_output.append(f"第{line_number}行{section_text}。")
        
        # 檢查是否整行都是休息
        all_rest = all(m.get("is_rest", False) for m in measures)
        if all_rest and measures:
            rest_count = len(measures)
            lines_output.append(f"休息{rest_count}個小節。")
            lines_output.append("")
            continue
        
        # 逐小節處理
        for measure in measures:
            measure_num = measure.get("measure_number", "?")
            is_rest = measure.get("is_rest", False)
            
            if is_rest:
                lines_output.append(f"第{measure_num}小節，休息。")
                continue
            
            # 轉換口訣
            events = measure.get("events", [])
            has_hihat = measure.get("has_hihat", False)
            syllables = events_to_syllables(events, has_hihat)
            
            # 偵測難點
            difficulties = detect_difficulty(measure)
            
            # 組合輸出
            if difficulties:
                diff_text = "，".join(difficulties)
                lines_output.append(f"第{measure_num}小節，{syllables}。這小節有{diff_text}。")
            else:
                lines_output.append(f"第{measure_num}小節，{syllables}。")
        
        lines_output.append("")
    
    return "\n".join(lines_output)


def parse_drum_sheet(image_paths: list[Path], output_dir: Path, model: str = "gemini-3-pro-preview") -> dict:
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

    # 步驟 3：生成講解逐字稿
    print("\n[步驟 3] 生成講解逐字稿...")
    transcript = generate_transcript(parsed_data)
    transcript_path = output_dir / f"{song_name}_講解稿.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"完成，已儲存至 {transcript_path.name}")


if __name__ == "__main__":
    main()
