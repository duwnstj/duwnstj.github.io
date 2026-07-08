---
title: "[AWS SRE 대서사시 3/4] Terraform State 기억상실증과 Import 복구기"
date: 2026-07-08 11:00:00
categories: [Tech Log]
tags: [AWS, Terraform, SRE, Troubleshooting]
---

# 🚀 AWS SRE 대서사시 3/4: 상태 불일치(Drift) 극복

> 이 글은 인프라 구축부터 CI/CD 배포까지 이어지는 SRE 트러블슈팅 대서사시의 세 번째 파트입니다.
> - [1/4] Terraform 파괴의 나비효과: VPC 철거 딜레이와 소크라테스 디버깅
> - [2/4] DNS 권한 위임과 ACM 전파 지연 트러블슈팅
> - **[3/4] Terraform State 기억상실증과 Import 복구기** (현재 글)
> - [4/4] 무중단 배포의 덫: GitHub Actions와 CodeDeploy 캐시 트러블슈팅

## 1. Deep Dive: "Already Exists" 에러와 Import 강제 입양 작전
이전 편에서 DNS 지연으로 인한 Terraform 무한 대기를 강제로 끊어냈을 때 발생한 또 다른 후폭풍입니다.

- **상황**: 무한 대기 중이던 Terraform을 `Ctrl+C`로 강제 종료했더니 상태 잠금(State Lock)이 걸렸습니다. Lock을 풀고 재배포를 쏘자, 이번엔 `Already exists` (이미 해당 A 레코드가 존재함) 충돌 에러가 발생했습니다.
- **나의 고민**: 실제 클라우드에는 레코드가 생겼는데, Terraform 장부(State)에는 뼈대가 안 적혀서 생긴 기억상실증 현상. 해결책은 3가지가 있었습니다.
  1. 콘솔에 가서 수동으로 지운다. (ClickOps 안티패턴)
  2. 코드를 모듈별로 더 잘게 쪼갠다.
  3. `terraform import`로 강제로 장부에 입양시킨다.
- **나의 결단**: 3번! 운영 환경(Prod)의 리소스를 마우스로 함부로 지우는 짓은 SRE에게 사형선고나 다름없습니다. 터미널에 `terraform import aws_route53_record.www ...` 명령을 치고 기존 자원을 안전하게 코드의 세계로 끌어안았습니다.

## 2. 파인만 비유 부록
- **Terraform State 기억상실증**: 현실의 공사판에는 철근이 세워져 있는데, 건축 현장 장부(State)에는 기록이 안 되어 있어 다음 날 인부가 "어? 철근이 이미 있는데 어떡하죠?" 라며 작업(Apply)을 멈춰버린 상황.
- **Route53(철근)과 ALB(전구)의 수명 주기**: 철근은 한 번 지으면 부술 일이 없지만, 전구는 수시로 갈아 끼웁니다. 이를 하나의 Terraform 장부(모놀리식)에 적어두면 전구를 갈다가 철근까지 흔들리는 대참사가 발생합니다. 이게 바로 실무에서 State Layering(base/app 분리)이 필수적인 이유입니다.

## 3. Trade-off (기술적 의사결정)
| 결정 사항 | 포기한 것 (Cons) | 얻은 것 (Pros) |
| --- | --- | --- |
| **Blog Queue 패턴 (MSA)** | 모놀리식 단일 폴더의 직관적 관리 | 실습(infra)과 블로그 엔진 간의 깃허브 충돌 방지 및 결합도 완벽 분리 |
| **`terraform import` 수동 복구** | 콘솔 삭제(ClickOps)의 빠름과 편리함 | 인프라 코드의 무결성(SSOT) 100% 방어 및 SRE 실무형 State 관리 역량 획득 |

## 4. STAR-F Q&A (실전 면접 방어)

**Q. IaC(Terraform)로 인프라를 관리할 때, 장부(State)와 실제 클라우드 상태가 어긋난(Drift) 경험이 있나요? 어떻게 해결하셨습니까?**
**A. (Situation)** 가비아에서 AWS로 DNS를 위임하고 ACM 인증서를 발급받는 과정에서, DNS 글로벌 전파 지연으로 Terraform 배포가 Hang(무한 대기) 상태에 빠졌습니다. 이를 강제 종료(SIGINT)하는 과정에서 AWS 클라우드에는 A 레코드가 생성되었지만 Terraform State 장부에는 기록되지 않는 상태 불일치(Drift)가 발생했습니다.
**(Task)** 재배포 시 발생하는 `Already exists` 충돌 에러를 해결하고, 끊어진 장부의 무결성을 다시 100%로 맞춰야 했습니다.
**(Action)** 가장 쉬운 방법은 AWS 콘솔에 들어가 마우스로 레코드를 삭제(ClickOps)하는 것이었지만, 이는 운영 인프라 관점에서는 절대 해선 안 될 안티패턴이라고 판단했습니다. 대신, `terraform import` 명령어를 활용해 이미 생성된 A 레코드의 ARN을 명시적으로 지정하여 Terraform State로 안전하게 강제 병합(Sync)시켰습니다.
**(Result & Follow-up)** 그 결과, 기존 인프라를 파괴하지 않고도 코드와 현실의 100% 동기화를 이루어냈습니다. 이 트러블슈팅을 통해 Route53(수명이 긴 자원)과 ALB/인증서(자주 바뀌는 자원)의 라이프사이클 차이를 인지하게 되었으며, 추후 실무에서는 State Layering(base/app 분리)을 통해 이런 결합도 문제를 원천 차단해야겠다는 SRE적 인사이트를 얻었습니다.
