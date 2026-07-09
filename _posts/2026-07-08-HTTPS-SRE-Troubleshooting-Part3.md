---
title: "[AWS SRE 대서사시 3/4] Terraform State 기억상실증과 Import 복구기"
date: 2026-07-08 11:00:00
categories: [Tech Log]
tags: [AWS, Terraform, SRE, Troubleshooting]
---

# 🚀 AWS SRE 대서사시 3/4: 상태 불일치(Drift) 극복

> 이 글은 인프라 구축부터 CI/CD 배포까지 이어지는 SRE 트러블슈팅 대서사시의 세 번째 파트입니다.
> - [1/4] Terraform 파괴의 나비효과: 상태 불일치(Drift)와 소크라테스 디버깅
> - [2/4] DNS 권한 위임과 ACM 전파 지연 트러블슈팅
> - **[3/4] Terraform State 기억상실증과 Import 복구기** (현재 글)
> - [4/4] 무중단 배포의 덫: GitHub Actions와 CodeDeploy 캐시 트러블슈팅

## 1. Deep Dive: "Already Exists" 에러와 Import 강제 입양 작전
이전 편에서 DNS 지연으로 인한 Terraform 무한 대기를 강제로 끊어냈을 때 발생한 또 다른 후폭풍입니다.

- **증상**: 무한 대기 중이던 Terraform을 강제 종료(SIGINT)했더니 상태 잠금(State Lock)이 걸렸습니다. Lock을 풀고 재배포를 쏘자, 이번엔 `Already exists` (이미 해당 A 레코드가 존재함) 충돌 에러가 발생했습니다. 클라우드 현실에는 A 레코드가 존재하지만 State 장부에는 누락된 기억상실 상태입니다.
- **분석**: Route53(철근)과 EC2/ALB(전구)의 Lifecycle이 다름을 깨닫고, 실무에서는 State Layering(base/app 분리)이 필수임을 인지했습니다.

## 2. 🗣️ 소크라테스 디버깅 일지 (AI와의 치열한 티키타카 및 사고 과정)

### 💬 에피소드 2. "Already Exists" 에러 앞에서의 3지 선다
- **마주친 에러**: 무한 대기를 강제 종료하고 직접 `terraform force-unlock`으로 잠금을 풀었다. 하지만 재실행 시 이미 A 레코드가 존재한다는 `Already exists` 충돌이 발생했다. 클라우드 현실에는 자원이 생겼는데 장부(State)엔 없는 상태였다.
- **AI 튜터의 뼈때리는 역질문**: *"이 상태 불일치를 해결할 3가지 방법이 있습니다. 어떻게 복구할 것인가요? 1. 콘솔에서 지운다(ClickOps) 2. 모듈을 분리한다 3. 코드로 강제 편입시킨다"*
- **나의 치열한 논리 전개**: 
  *"1. 모듈을 또 분리한다? 2. 모듈들을 더 세부적으로 나눈다? 알겠는데 그러면 지금 우리 파일 구조를 저렇게 만든다면 생기는 문제점은 파일 관리의 복잡성이지. 그렇다고 운영 환경 자원을 콘솔에서 함부로 마우스로 지우는 건 SRE가 할 짓이 아니야."*
- **나의 Aha-Moment (결단)**: *"정답은 3번. 기존 자원을 파괴하지 않고 장부에 편입시키는 `terraform import`를 쓸 것 같아!"* 과감히 명령을 날렸고, 기존 A 레코드를 안전하게 코드에 입양시키며 *"어, 적용 성공이야!"*라는 쾌감을 맛보았다.

## 3. 파인만 비유 부록
- **Terraform State 기억상실증**: 현실의 공사판에는 철근이 세워져 있는데, 건축 현장 장부(State)에는 기록이 안 되어 있어 다음 날 인부가 "어? 철근이 이미 있는데 어떡하죠?" 라며 뻗어버린 상황. `Import`는 장부에 "그 철근 우리 거 맞아!"라고 도장을 찍어주는 과정입니다.

## 4. Trade-off (기술적 의사결정)
| 결정 사항 | 포기한 것 (Cons) | 얻은 것 (Pros) |
| --- | --- | --- |
| **`terraform import` 수동 복구** | 콘솔 삭제(ClickOps)의 빠름과 편리함 | 인프라 코드의 무결성(SSOT) 확보 및 실무형 State 관리 역량 |

## 5. STAR-F Q&A (면접 방어)

**Q. IaC(Terraform)로 인프라를 관리할 때, 장부(State)와 실제 클라우드 상태가 어긋난(Drift) 경험이 있나요? 어떻게 해결하셨습니까?**
**A. (Situation)** 가비아에서 AWS로 DNS를 위임하고 ACM 인증서를 발급받는 과정에서 DNS 전파 지연으로 인해 배포가 Hang(무한 대기) 상태에 빠졌고, 강제 종료 과정에서 클라우드에는 리소스가 생성되었으나 State 장부에는 누락되어 `Already exists` 충돌이 발생했습니다.
**(Task)** State 락을 해제하고, 캐싱된 인증서를 우회하며, 누락된 상태를 동기화해야 했습니다.
**(Action)** 첫째, Lock이 걸린 State를 `terraform force-unlock`으로 직접 해제했습니다. 둘째, 가장 직관적인 마우스 삭제(ClickOps)의 유혹을 뿌리치고, `terraform import` 명령을 통해 생성된 A 레코드를 State에 안전하게 복구했습니다. 셋째, 멀쩡한 Route53 인프라는 보존하면서 불량 인증서만 `terraform apply -replace` 명령으로 강제 재생성(Taint)하여 10초 만에 DNS 검증을 패스했습니다.
**(Result & Follow-up)** 그 결과 SRE 원칙에 위배되는 수동 조작 없이 100% 코드로 무결성을 회복했으며, 이를 통해 Route53(철근)과 ALB(전구)의 라이프사이클 차이를 절감하고 State를 계층적으로 분리(Layering)해야 한다는 실무적 인사이트를 얻었습니다.
