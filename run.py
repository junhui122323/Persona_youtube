import os
import json
import ollama
import uvicorn
import yt_dlp
import requests
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from jinja2 import Template

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Persona AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;700&display=swap');
        body { font-family: 'Pretendard', sans-serif; }
    </style>
</head>
<body class="bg-slate-900 text-white p-10 font-sans">
    <div class="max-w-3xl mx-auto text-center">
        <header class="mb-10">
            <h1 class="text-4xl font-bold mb-2 text-blue-400">📺 유튜브 페르소나 분석기</h1>
            <p class="text-slate-500 text-sm tracking-widest uppercase text-center">Ollama + Transcript Monitoring</p>
        </header>
        
        <form action="/analyze" method="post" class="flex gap-2 mb-10 bg-slate-800 p-2 rounded-xl border border-slate-700">
            <input type="text" name="url" placeholder="유튜브 주소 입력" required 
                   class="flex-1 p-3 rounded bg-transparent outline-none text-white text-left">
            <button type="submit" class="bg-blue-600 hover:bg-blue-500 px-8 py-3 rounded-lg font-bold transition">분석 시작</button>
        </form>

        {% if result %}
        <div class="space-y-6 text-left animate-in fade-in duration-500">
            <div class="bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-xl">
                <h2 class="text-xl font-bold mb-3 text-emerald-400 text-center uppercase">📌 AI 분석 리포트</h2>
                <div class="bg-slate-900 p-6 rounded-xl border border-slate-700">
                    <h3 class="text-xs font-bold text-slate-500 mb-2 uppercase tracking-widest">핵심 요약</h3>
                    <p class="text-slate-300 leading-relaxed text-lg">{{ result.summary }}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                {% for p in result.personas %}
                <div class="bg-slate-800 p-5 rounded-xl border border-slate-700 hover:border-blue-500 transition shadow-lg">
                    <div class="text-3xl mb-4 text-center">👤</div>
                    <h3 class="font-bold text-lg mb-1 text-center">{{ p.name }}</h3>
                    <p class="text-xs text-blue-400 mb-3 font-semibold uppercase text-center border-b border-slate-700 pb-2">{{ p.trait }}</p>
                    <p class="text-sm text-slate-400 italic">"{{ p.comment }}"</p>
                    <div class="mt-4 text-right font-bold text-blue-500 text-lg">{{ p.score }}%</div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_transcript_via_ytdlp(url):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['ko', 'en'],
        'quiet': True,
        'cookiesfrombrowser': ('chrome',),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subtitles = info.get('requested_subtitles')
        
        if subtitles:
            lang = list(subtitles.keys())[0]
            sub_url = subtitles[lang]['url']
            res = requests.get(sub_url)
            # JSON 데이터일 경우 텍스트만 추출하는 간단한 전처리 (Ollama용)
            return res.text
        return None

@app.get("/", response_class=HTMLResponse)
async def index():
    return Template(HTML_TEMPLATE).render(result=None)

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(url: str = Form(...)):
    print("\n" + "="*50)
    print(f"🚀 분석 프로세스 가동: {url}")
    
    try:
        t_text = get_transcript_via_ytdlp(url)
        
        if not t_text:
            print("❌ 자막을 찾을 수 없습니다.")
            return "<h2>자막을 찾을 수 없습니다.</h2>"

        # [추가] 터미널에 자막 내용 출력 (앞부분 500자)
        print("-" * 50)
        print("📝 수집된 자막 미리보기 (Terminal Monitoring):")
        print(f"{t_text[:500]}...") # 자막의 앞부분 500자만 출력
        print("-" * 50)
        print(f"✅ 자막 로드 완료! (총 {len(t_text)}자)")

        print("🧠 Ollama(Llama3) 분석 시작...")
        prompt = f"""유튜브 자막 데이터: {t_text[:3000]}
        위 내용을 분석해서 서로 다른 성향을 가진 시청자 페르소나 3명의 반응을 한국어로 작성해줘.
        결과는 반드시 아래 JSON 형식으로만 출력해:
        {{ "summary": "영상 핵심 3줄 요약", "personas": [{{ "name": "이름", "trait": "성향", "score": 90, "comment": "소감" }}] }}
        """
        
        res = ollama.generate(model='llama3', prompt=prompt, format='json')
        data = json.loads(res['response'])
        
        print("✨ 분석 완료!")
        print("="*50 + "\n")

        return Template(HTML_TEMPLATE).render(result={
            "summary": data.get("summary", ""),
            "personas": data.get("personas", [])
        })

    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        return f"<h2>분석 실패</h2><p>에러: {e}</p>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)