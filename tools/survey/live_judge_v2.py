import os, json, csv, sys, urllib.request

def call_gemini(text_sample, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    prompt = f"당신은 소설 품질 감리관입니다. 아래 수치와 경로의 데이터가 기계적 반복(석화)인지 판결하세요. 결과는 '유죄/무죄' 명시와 '이유'를 3줄 내로 쓰세요.\n\n{text_sample}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())['candidates'][0]['content']['parts'][0]['text']

def run(run_dir, api_key):
    csv_path = os.path.join(run_dir, "matrix_r1.csv")
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    
    # [FIX] 컬럼명을 'S09'로 정확히 타격 (KeyError 해결)
    top_20 = sorted(rows, key=lambda x: float(x.get('S09', 0)), reverse=True)[:20]
    
    judgments = []
    for i, candidate in enumerate(top_20):
        print(f"[*] Judging Candidate {i+1}/20: {candidate['path']}")
        # 실제 데이터 기반 판결 요청
        msg = f"Path: {candidate['path']}, S09_Score: {candidate.get('S09')}, Level: {candidate.get('window_level')}"
        res = call_gemini(msg, api_key)
        judgments.append({"slot": candidate['slot'], "path": candidate['path'], "score": candidate['S09'], "verdict": res})

    with open(os.path.join(run_dir, "topN_candidates.json"), "w", encoding='utf-8') as f:
        json.dump(judgments, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run(r'C:\g7core\g7_v1\runs\STRICT_STAIR_1623', 'AIzaSyBreX9jWMmxzCD7aySlpZ2I3PJUmcY1AgY')
