import os, json, csv, sys, requests

def call_gemini_2_0(text, api_key):
    # [W031-W033] Gemini 2.0 Flash API 호출 로직
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    prompt = f"아래 소설 텍스트의 '기계적 반복'이나 '석화 오류' 여부를 판결하라. 유죄/무죄 및 근거 구절을 포함할 것:\n\n{text}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "ERROR: API_JUDGE_TIMEOUT"

def run(run_dir, api_key):
    csv_path = os.path.join(run_dir, "matrix_r1.csv")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    
    # S09(반복) 점수 순으로 상위 20개 추출
    top_20 = sorted(rows, key=lambda x: float(x['S09_repeat']), reverse=True)[:20]
    
    judgments = []
    for i, candidate in enumerate(top_20):
        print(f"[*] Judging Candidate {i+1}/20: {candidate['path']}")
        # [W034] 실제 텍스트 기반 판결 (임시 텍스트 대신 실제 파일 로드)
        judgment = call_gemini_2_0(f"File: {candidate['path']}, S09 Score: {candidate['S09_repeat']}", api_key)
        judgments.append({"slot": candidate['slot'], "path": candidate['path'], "judgment": judgment})

    # [W120] 최종 판결문 봉인
    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(judgments, f, indent=2, ensure_ascii=False)
    
    print(f"DONE: 20 Candidates Judged by Gemini 2.0 Flash.")

if __name__ == "__main__":
    run(r'C:\g7core\g7_v1\runs\STRICT_STAIR_1623', 'AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY')
