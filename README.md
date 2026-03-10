# 📺 YouTube Persona Analyzer (Fersona)
> **Ollama(Llama3)** 기반 로컬 LLM을 활용한 유튜브 시청자 페르소나 분석 엔진

이 프로젝트는 유튜브 영상의 자막(Transcript)을 추출하여 AI가 시청자의 반응을 예측하고, 3가지 서로 다른 성향의 페르소나 리포트를 생성하는 웹 애플리케이션입니다. **M2 MacBook Air** 환경에 최적화되어 로컬에서 개인 정보 유출 없이 분석이 가능합니다.

---

## 🚀 주요 기능
* **자막 자동 추출**: `yt-dlp`를 활용하여 영상의 자막 데이터를 실시간 수집
* **AI 페르소나 생성**: Ollama(Llama3)를 사용하여 3인의 가상 시청자 반응 생성
* **핵심 요약**: 영상 전체 내용을 3줄로 요약하여 인사이트 제공
* **반응형 UI**: Tailwind CSS를 활용한 깔끔하고 직관적인 대시보드

---

## 🛠 기술 스택
* **Backend**: FastAPI (Python 3.9+)
* **AI Engine**: Ollama (Llama3 Model)
* **Library**: yt-dlp, uvicorn, jinja2
* **Frontend**: Tailwind CSS

---

## ⚙️ 설치 및 실행 방법

### 1. 전제 조건
* [Ollama](https://ollama.com/) 설치 및 `llama3` 모델 다운로드 완료
  ```bash
  ollama pull llama3