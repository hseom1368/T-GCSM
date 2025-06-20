# T-GCSM v2.0: Taiwan Ground Combat Simulation Model

## 개요

T-GCSM(Taiwan Ground Combat Simulation Model) v2.0은 CSIS(Center for Strategic and International Studies) 보고서 "The First Battle of the Next War: Wargaming a Chinese Invasion of Taiwan"에 기반한 턴 기반 헥사고날 워게임 시뮬레이션입니다.

이 모델은 2026년 중국의 대만 침공 시나리오 중 지상전 구성 요소를 모델링하며, 투명성과 재현성을 보장하기 위해 객체 지향 프로그래밍과 엄격한 규칙 기반 판정 원칙에 따라 구축되었습니다.

## 주요 특징

- **턴 기반 시뮬레이션**: 각 턴은 3.5일을 나타내며, 최대 10턴(35일)까지 진행
- **헥사고날 그리드**: 대만 전역을 30km 헥스로 표현
- **두 진영**: PLA(중국 인민해방군)와 ROC(중화민국/대만)
- **AI 확장성**: 인간 플레이어, 스크립트 AI, 또는 LLM 기반 AI 에이전트 지원
- **데이터 기반 모델링**: 실제 군사 장비 제원과 부대 편성 데이터 활용
- **모듈화 설계**: 유지보수와 확장이 용이한 구조

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/tgcsm-v2.git
cd tgcsm-v2
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. (선택사항) 개발 모드 설치
```bash
pip install -e .
```

## 사용 방법

### 기본 실행 (AI vs AI)
```bash
python run_simulation.py
```

### 인간 vs AI
```bash
python run_simulation.py --pla-agent human --roc-agent ai
```

### 결과 데이터 내보내기
```bash
python run_simulation.py --export game_results
```

### Python 스크립트에서 사용
```python
from tgcsm import load_data, SimulationEngine, ScriptedAgent, print_final_summary

# 데이터 로드
data = load_data()

# 엔진 생성 (AI vs AI)
engine = SimulationEngine(data, ScriptedAgent, ScriptedAgent)

# 시뮬레이션 실행
engine.run_simulation()

# 결과 출력
print_final_summary(engine)
```

### Google Colab에서 사용
```python
# 저장소 클론
!git clone https://github.com/yourusername/tgcsm-v2.git
!cd tgcsm-v2 && pip install -r requirements.txt

# 시뮬레이션 실행
!cd tgcsm-v2 && python run_simulation.py
```

## 프로젝트 구조

```
tgcsm-v2/
├── README.md                 # 이 파일
├── requirements.txt          # Python 의존성
├── run_simulation.py        # 메인 실행 스크립트
│
├── tgcsm/                   # 메인 패키지
│   ├── __init__.py         # 패키지 초기화
│   ├── config.py           # 설정 및 상수
│   ├── enums.py            # Enum 정의
│   ├── data_loader.py      # 데이터 로딩
│   ├── models.py           # Hex, Unit 클래스
│   ├── agents.py           # AI 에이전트
│   ├── engine.py           # 시뮬레이션 엔진
│   └── analysis.py         # 분석 함수
│
└── examples/               # 예제 스크립트
    ├── run_ai_vs_ai.py
    └── run_human_vs_ai.py
```

## 게임 규칙

### 턴 구조
각 턴은 다음 단계로 구성됩니다:

1. **공중 및 해상 효과 단계**: 차단 작전, 상륙 능력 감소 등
2. **보급 상태 결정 단계**: 각 유닛의 보급선 확인
3. **플레이어 행동 단계**: PLA가 먼저, 그 다음 ROC가 행동
4. **전투 판정 단계**: 모든 전투를 동시에 해결
5. **군수 및 증원 단계**: PLA 증원 부대 상륙
6. **턴 종료 및 승리 조건 확인**: 게임 종료 조건 체크

### 승리 조건
- **PLA 승리**: 타이베이(Taipei) 점령
- **ROC 승리**: 10턴 동안 생존 또는 모든 PLA 부대 제거

### 유닛 유형
- **Armor**: 기갑 (높은 공격력, 중간 이동력)
- **Mechanized**: 기계화보병 (균형잡힌 능력)
- **Infantry**: 보병 (높은 방어력, 낮은 이동력)
- **Artillery**: 포병 (간접 지원)
- **Engineer**: 공병 (특수 능력)
- **AttackHelo**: 공격헬기 (높은 이동력)

## 개발 및 확장

### 새로운 AI 에이전트 추가
```python
from tgcsm.agents import Agent

class MyCustomAgent(Agent):
    def choose_actions(self, game_state, possible_actions):
        # 커스텀 AI 로직 구현
        return selected_actions
```

### LLM 기반 에이전트 예제
```python
class LLMAgent(Agent):
    def __init__(self, faction, engine, llm_model):
        super().__init__(faction, engine)
        self.llm = llm_model
    
    def choose_actions(self, game_state, possible_actions):
        # LLM에 게임 상태 전달하고 행동 선택
        prompt = self.format_game_state(game_state)
        response = self.llm.generate(prompt)
        return self.parse_llm_response(response)
```

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다. CSIS 보고서의 공개 데이터와 방법론을 기반으로 하며, 실제 군사 작전이나 정책 결정에 사용되어서는 안 됩니다.

## 기여 방법

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 참고 문헌

- CSIS Report: "The First Battle of the Next War: Wargaming a Chinese Invasion of Taiwan"
- 기술 명세서: "대만 지상전 시뮬레이션 모델 T-GCSM v2.0 기술 명세 및 코딩 작업 지시서"

## 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 Issues 섹션을 이용해 주세요.