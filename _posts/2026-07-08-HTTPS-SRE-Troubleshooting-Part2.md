---
title: "[AWS SRE 대서사시 2/3] Terraform State 기억상실증과 Import 복구기"
date: 2026-07-08 11:00:00
categories: [Tech Log]
tags: [AWS, Terraform, SRE, Troubleshooting]
---

# 🚀 AWS SRE 대서사시 2/3: 인프라 상태 복구하기

> 이 글은 인프라 구축부터 CI/CD 배포까지 이어지는 SRE 트러블슈팅 대서사시의 두 번째 파트입니다.
> - [1/3] DNS 권한 위임과 ACM 전파 지연 트러블슈팅
> - **[2/3] Terraform State 기억상실증과 Import 복구기** (현재 글)
> - [3/3] 무중단 배포의 덫: GitHub Actions와 CodeDeploy 캐시 트러블슈팅

## 1. 전편 요약과 새로운 위기
1편에서 ACM 인증서 발급 무한 대기 현상(Hang)을 마주쳤을 때, 배포를 멈추기 위해 강제 종료(Ctrl+C)를 감행했습니다. 그 결과 **클라우드 상에는 A 레코드 리소스가 이미 만들어졌으나, 로컬 Terraform State 장부에는 누락되어버리는 '기억상실'** 상태가 초래되었습니다.

## 2. Deep Dive: Terraform State 기억상실증과 Import 강제 입양

### 💥 트러블슈팅 상황
- **증상**: 코드를 재실행(Apply)하자, "해당 도메인의 A 레코드가 이미 존재한다(already exists)"며 충돌 에러를 뱉어내고 배포가 완전히 멈춰버렸습니다.
- **분석**: Route53과 EC2/ALB의 Lifecycle이 다르기 때문에 발생한 문제였습니다. 실무에서는 이처럼 Lifecycle이 다른 리소스들의 State Layering(base/app 분리)이 필수적이라는 뼈아픈 교훈을 얻었습니다.
- **해결**: 콘솔에 직접 접속해서 리소스를 몰래 지워버리는 ClickOps 안티패턴 유혹을 참아냈습니다. 대신, `terraform import` 명령어를 사용하여 실제 AWS 클라우드에 둥둥 떠다니는 고아 리소스(A 레코드)를 코드의 장부에 안전하게 강제 복구(Sync)하는 데 성공했습니다.

## 3. Trade-off (기술적 의사결정)
| 결정 사항 | 포기한 것 (Cons) | 얻은 것 (Pros) |
| --- | --- | --- |
| **`terraform import` 수동 복구** | AWS 콘솔 접속 후 삭제(ClickOps)의 빠름과 일시적 편리함 | 인프라 코드의 완벽한 무결성(SSOT) 확보 및 실무형 State 관리 역량 경험 |

## 4. 파인만 비유 부록 (Feynman Analogy)
- **Terraform 4대장**: 
  - `variables.tf`: 건축에 필요한 공사 자재 스펙
  - `main.tf`: 건물을 어떻게 지을지 그려놓은 건축 설계도
  - `provider.tf`: 공사를 대행해 줄 외주 건설 업체 (AWS)
  - `outputs.tf`: 완공 후 발급받는 영수증 (IP 주소 등)

## 5. STAR-F Q&A (면접 방어)
**Q. 인프라 코드를 짤 때 Terraform State 충돌이나 지연 문제가 발생한 적 있나요? 어떻게 해결했습니까?**
**A. (Situation)** 가비아에서 AWS로 DNS를 위임하고 ACM 인증서를 발급받는 과정에서 DNS 전파 지연으로 인해 Terraform이 Hang 상태에 빠졌고, 강제 종료 과정에서 `already exists` 충돌이 발생했습니다.
**(Task)** State 락을 해제하고, 캐싱된 인증서를 우회하며, 누락된 상태를 동기화해야 했습니다.
**(Action)** 첫째, 비상 권한으로 `force-unlock`을 수행했습니다. 둘째, ClickOps 삭제를 피하고 `terraform import` 명령을 통해 A 레코드를 State에 안전하게 복구했습니다. 셋째, 멀쩡한 Route53 인프라는 보존하면서 불량 인증서만 `terraform apply -replace` 명령으로 강제 재생성(Taint)하여 10초 만에 DNS 검증을 패스했습니다.
**(Result & Follow-up)** 그 결과 SRE 원칙에 위배되는 수동 개입 없이 100% 코드로 무결성을 회복했으며, State를 계층적으로 분리(Layering)하는 실무적 인사이트를 얻었습니다.

> **다음 편 예고**: 드디어 단단한 인프라 뼈대가 완성되었습니다. 이제 애플리케이션 코드를 얹어 배포할 차례입니다. 하지만 GitHub Actions와 CodeDeploy가 그리는 무중단 배포의 환상은 캐시 충돌이라는 복병에 산산조각 납니다. CI/CD의 처절한 트러블슈팅을 3편에서 만나보세요! 👉 **[3편으로 이어짐]**
