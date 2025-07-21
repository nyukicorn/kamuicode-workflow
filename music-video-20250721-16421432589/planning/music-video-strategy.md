# 음악비디오 제작 전략서 - 월광의 하니 재즈피아노

## 基本設定
- **音声コンセプト**: 완전수정판테스ト: 월광下の Jazz Piano
- **制約条件**: 동영상 5초×3개，음악30-40초
- **전략적목표**: 제한된 소재로최大효과실현

## 音樂生成戦略

### Google Lyria向프롬프터設定
```
Moonlit jazz piano ballad, sophisticated night atmosphere, 30-40 seconds short format, gentle romantic mood, featuring elegant piano melody with subtle double bass accompaniment, soft jazz drums, ambient moonlight soundscape, medium tempo 90-110 BPM, lounge style, dreamy nocturnal vibes, sophisticated harmony progressions, gentle dynamics with emotional crescendo, perfect for background music, intro-style composition
```

### 音樂구성분석 (30-40초)
- **0-8초**: 피아노인트로，부드러운분위기설정
- **8-15초**: 베이스추가，메인멜로디시작
- **15-25초**: 클라이맥스，풍부한편성
- **25-32초**: 멜로디變化，솔로部分
- **32-40초**: 終結，페이드아웃

## 動画戦략設計

### 動画役割분담
1. **動画1 (메인 50-60%사용)**
   - 사용시간: 0-8초, 15-25초, 35-40초 (총 18-24초)
   - 역할: 기본적인분위기・테마표현
   - 내용: 피아노연주손클로저업

2. **動画2 (액센트 20-30%사용)**
   - 사용시간: 8-15초, 25-32초 (총 6-12초)
   - 역할: 클라이맥스・전환점担当
   - 내용: 재즈클럽분위기와이드샷

3. **動画3 (트랜지션 10-20%사용)**
   - 사용시간: 간주및변화점 3-5회삽입 (총 3-8초)
   - 역할: 이음・변화演出
   - 내용: 추상적월광패턴

### 편집최적화전략

#### Loop対応設計
- **시작・종료점 자연연속**: 각동영상순환재생가능설계
- **템포적응**: 음악의비트와동기화
- **감정변화대응**: 동영상전환이음악감정변화와일치

#### 速度調整계획
- **動画1**: 0.5-1.5배속，피아노연주자연성유지
- **動画2**: 0.8-2.0배속，분위기변화강조
- **動画3**: 0.3-2.0배속，트랜지션효과최대화

#### エフェクト活용
- **필터**: 월광분위기강조를위한블루・실버톤
- **트랜지션**: 부드러운페이드인・아웃
- **오버레이**: 월빛효과추가가능

## 画像生成전략

### Imagen 4 Fast対応프롬프터
```
Elegant jazz piano scene under moonlight, sophisticated nighttime atmosphere, soft silver moonbeams illuminating black grand piano, ambient blue-purple nocturnal lighting, romantic dreamy mood, cinematic depth of field, luxury jazz club ambiance, moody shadows and highlights, artistic composition with emotional depth, perfect for jazz ballad visualization, high quality aesthetic
```

### 시각적일관성유지
- **색채팔레트**: 블루・실버・퍼플의야간색조
- **조명설정**: 월빛을중심으로한소프트라이팅
- **구성**: 피아노를중심으로한우아한배치

## 영상コンセプト상세

### Hailuo-02 Pro対応설정
각동영상은5초제한내에서최대효과달성：

#### 動画1 (메인)
```
Smooth piano playing hands close-up, elegant finger movements, seamless loop, 0.5-2x speed adaptable, soft lighting transitions
```

#### 動画2 (액센트)
```
Jazz club atmosphere wide shot, subtle lighting changes, emotional peak moments, speed variations for crescendo
```

#### 動画3 (트랜지션)
```
Abstract moonlight patterns, gentle movements, bridge connections, perfect for speed adjustments and fade effects
```

## 제작스케줄

1. **音樂생성** (Google Lyria)
2. **画像생성** (Imagen 4 Fast) 
3. **動画생성** (Hailuo-02 Pro - 3회실행)
4. **편집・조합** (최적화된배치로조합)
5. **최종검수** (음악과동영상동기화확인)

## 성공評価指標

- **음향품질**: 재즈피아노의우아함표현
- **시각적효과**: 월광분위기재현도  
- **편집완성도**: 자연스러운전환과루프
- **전체적합성**: 음악과영상의완벽한조화

## 주의사항

- **시간제약준수**: 각단계에서제한시간엄격관리
- **품질우선**: 제한된소재로최고품질달성
- **일관성유지**: 전체컨셉트일치성확보