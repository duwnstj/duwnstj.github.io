---
layout: post
title: "기본 VPC를 버리다: 퍼블릭/프라이빗 망 분리부터 Lambda 서버리스 슬랙 알람까지"
date: 2026-07-02 12:30:00 +0900
categories: [DevOps, AWS, FinOps, Serverless]
tags: [VPC, Subnet, Lambda, SNS, CloudWatch, SlackWebhook]
mermaid: true
---

## 🚀 면접관을 위한 3줄 요약 (STAR-F)

- **Situation (상황):** 기존의 AWS Default VPC에 의존하던 불안정한 튜토리얼 수준의 인프라를 실무 엔터프라이즈 환경에 맞게 재설계해야 했음.
- **Task (과제):** 외부 공격을 차단하는 **VPC 망 분리 아키텍처**를 설계하고, 서버 메모리 이상(Leak) 발생 시 즉각적으로 개발팀 슬랙(Slack)으로 전파되는 **경고 파이프라인**을 마 편집기(ClickOps)만으로 수동 구축해야 함.
- **Action & Result (행동과 결과):** 
  - **FinOps 딜레마 극복:** Private Subnet을 구성할 경우 필연적으로 발생하는 NAT Gateway 과금(월 약 $30)을 방어하기 위해, 비용 최적화 측면에서 **Public Subnet + Security Group(80, 443 포트 통제)** 아키텍처로 타협안(Trade-off)을 도출.
  - **서버리스 파이프라인 구축:** AWS SNS의 Raw JSON 데이터가 Slack Webhook 규격과 호환되지 않는 문제를 해결하기 위해, 중간에 **AWS Lambda (Python)** 번역기를 끼워 넣어 완벽한 커스텀 알람 파이프라인 완성. 
- **FinOps (비용 최적화):** NAT Gateway(월 $30) 미사용 아키텍처 채택, 무거운 서드파티 모니터링 툴(Datadog 등) 대신 AWS Native(CloudWatch+Lambda)를 조합하여 모니터링 유지비 $0 달성.

---

## 💥 사건의 발단: "RDS도 없는데 굳이 망을 분리해야 하나요?"

모든 것은 아주 단순하고 원초적인 질문에서 시작되었다.

> **나:** "음? 지금 RDS(DB)도 안 쓰는데 굳이 Private 인프라랑 Public 인프라를 나눠서 구성할 필요가 있을까? 그냥 EC2 하나만 Public에 띄우면 안 되나?"
> 
> **AI 튜터:** "학원 실습이라면 그래도 됩니다. 하지만 실무 데브옵스 엔지니어라면 해커에게 소스코드가 담긴 안방을 그대로 내어줄 셈입니까? 편의를 위해 **보안(Network Isolation)**의 기초를 무시하면 안 됩니다. 기본 VPC를 당장 버리세요!"

그렇게 나는 마우스 클릭(ClickOps)만으로 **'나만의 가상 영토(VPC)'**를 바닥부터 파헤치는 고통스러운 수동 작업의 늪에 빠지게 되었다.

---

## 🤔 치열한 고민: 보안인가, 과금인가? (FinOps 딜레마)

튜터의 압박에 못 이겨 VPC(`10.0.0.0/16`)와 Subnet(`10.0.1.0/24`)을 수동으로 파기 시작했다. 
인터넷과 연결된 선착장(IGW)을 만들고 라우팅 테이블(0.0.0.0/0)을 연결하면서, 문득 아키텍처의 거대한 딜레마에 봉착했다.

**[딜레마: NAT Gateway의 살인적인 유지비]**
- **정석적인 실무 아키텍처:** App EC2는 외부 인터넷과 단절된 **Private Subnet**에 둔다.
- **문제점:** EC2 안에 설치된 `CloudWatch Agent`가 메모리 지표를 AWS로 보내거나, GitHub에서 소스코드를 Pull 해오려면 외부 인터넷으로 나갈 통로가 필요하다. 이를 위해 **NAT Gateway**를 Public Subnet에 두어야 한다.
- **FinOps의 벽:** NAT Gateway는 프리티어가 없으며, 숨만 쉬어도 **월 약 4만 원($30)**의 고정 과금이 발생한다. 포트폴리오나 초기 스타트업에게는 뼈아픈 지출이다.

**💡 나의 결단 (Trade-off):** 
DB(RDS)가 따로 없는 현 상황과 **'비용 최적화(FinOps)'**를 최우선으로 고려하여, 굳이 NAT Gateway를 쓰지 않고 EC2를 **Public Subnet**에 두기로 했다. 단, **보안 그룹(Security Group)**을 통해 80(HTTP), 443(HTTPS), 그리고 내 IP에서의 22(SSH) 포트만 엄격하게 열어두어 해커의 침입을 방어하는 합리적인 타협안을 선택했다. 면접관 앞에서도 당당히 방어할 수 있는 아키텍처 논리다.

```mermaid
graph TD
    subgraph "AWS Cloud (Custom VPC)"
        IGW[Internet Gateway]
        subgraph "Public Subnet (10.0.1.0/24)"
            SG[Security Group: 80, 443 Only]
            EC2[App EC2 Server<br>CloudWatch Agent]
        end
        IGW <--> |Route Table (0.0.0.0/0)| SG
        SG <--> EC2
    end
    EC2 -.-> |Metrics| CW(CloudWatch Alarm)
    style EC2 fill:#f9f,stroke:#333,stroke-width:2px
```

---

## 🛠️ 문제 해결: 무식한 SNS를 통역하는 서버리스(Lambda)

VPC를 만들고, User Data를 통해 EC2가 부팅될 때 알아서 CloudWatch Agent가 설치되도록 쉘 스크립트(`init-ec2.sh`)를 작성했다.

> [!TIP]
> **[User Data 에이전트 자동화 스크립트 핵심부]**
> EC2가 태어날 때 로컬 폴더를 마운트할 수 없으므로, Bash의 `HereDoc(cat << EOF)` 기법을 사용해 서버 부팅 시점에 즉각적으로 JSON 설정 파일을 동적 생성하도록 설계했다.

메모리 누수(80% 초과) 시 나에게 슬랙(Slack) 알람을 보내기 위해 **CloudWatch Alarm -> SNS** 파이프라인을 엮었다. 하지만 여기서 거대한 에러를 만났다.

**"SNS 프로토콜에 Slack이 없다?"**
SNS에 HTTPS로 슬랙 웹훅 URL을 그대로 박아 넣었더니 아무런 알람이 오지 않았다. 알고 보니 슬랙은 `{"text": "메시지"}` 형태의 예쁜 JSON을 기대하는데, AWS SNS는 자비 없는 거대한 메타데이터 덩어리를 쏘기 때문에 슬랙이 이를 뱉어낸 것이다.

이를 해결하기 위해 중간에 **AWS Lambda(서버리스 번역기)**를 도입했다. SNS가 Lambda를 찌르면, Lambda가 파이썬 코드로 데이터를 가공해 슬랙에 던져주는 파이프라인이다!

```python
# lambda-sns-to-slack.py (핵심 로직)
import urllib.request, json, os

def lambda_handler(event, context):
    slack_url = os.environ.get('SLACK_WEBHOOK_URL')
    
    # SNS가 보낸 무시무시한 JSON 속에서 알맹이(Message)만 빼내기
    sns_message = event['Records'][0]['Sns']['Message']
    subject = event['Records'][0]['Sns']['Subject'] or "AWS CloudWatch 알람 🚨"
    
    # 슬랙이 예쁘게 읽을 수 있는 포맷으로 데이터 재조립
    slack_data = { "text": f"*{subject}*\n```{sns_message}```" }
    
    # 외부 라이브러리(requests) 없이 내장 urllib으로 발송!
    req = urllib.request.Request(
        slack_url, data=json.dumps(slack_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)
    return {"status": 200, "message": "Success"}
```

결과는? **대성공.** 
메모리 테스트 임계값(10%)을 넘기자마자, 슬랙 봇이 정확하게 알람을 뱉어냈다! 🎉

---

## 🛡️ 셀프 기습 면접 (방어 논리)

**Q1. 왜 AWS Chatbot을 안 쓰고 굳이 귀찮게 Lambda를 썼나요?**
> "AWS Chatbot은 설정이 간편하지만 템플릿 커스터마이징에 한계가 있습니다. Lambda를 중간에 두면, 향후 메시지에 특정 대시보드 URL이나 분석 데이터를 덧붙여(Enrichment) 알림을 고도화할 수 있습니다. 또한, '이벤트 기반(Event-Driven) 서버리스 아키텍처'를 경험해 보기 위한 전략적 선택이었습니다."

**Q2. 서브넷 CIDR 블록 `/24`는 몇 개의 IP를 가지며, 실제로 쓸 수 있는 서버 수는 몇 개인가요?**
> "IPv4는 총 32비트이므로 `32 - 24 = 8`비트, 즉 2의 8승인 **256개**의 IP를 가집니다. 하지만 AWS 내부 규정상 네트워크 식별(0), 라우터(1), DNS(2), 예약(3), 브로드캐스트(255) 등 총 **5개의 IP를 몰래 선점**하기 때문에, 실제 가용 IP 수는 **251개**입니다."

**Q3. VPC, Subnet, Route Table 구성을 바다에 비유해 보세요.**
> "VPC는 나만의 **거대한 바다**입니다. Public Subnet은 그 바다 중에서 선착장(IGW)을 통해 외부(인터넷)로 나갈 수 있는 바다이고, Private Subnet은 선착장으로 가는 길이 없는 고립된 바다입니다. EC2는 그 바다 위에 떠 있는 **배**이며, Route Table은 배들이 선착장으로 갈 수 있도록 길을 알려주는 **해양 네비게이션**입니다."

---

이렇게 마우스 클릭만으로 피를 토하며(ClickOps) VPC망부터 서버리스 알람까지 모든 것을 바닥부터 쌓아 올렸다. 이제 이 고통을 해방시켜 줄 **Terraform(IaC)** 자동화의 세계로 넘어갈 준비가 모두 끝났다.
