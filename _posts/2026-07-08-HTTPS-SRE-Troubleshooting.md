---
title: "AWS HTTPS 인프라 구축과 SRE 트러블슈팅 대서사시"
date: 2026-07-08
tags: ["AWS", "Terraform", "CodeDeploy", "SRE", "FinOps", "Troubleshooting"]
---

# 🚀 AWS HTTPS 인프라 구축과 SRE 트러블슈팅 대서사시

## 1. 10초 요약 (TL;DR)
- 단순한 인프라 세팅을 넘어, **SRE(Site Reliability Engineering)** 관점에서 발생할 수 있는 캐시 충돌, Race Condition, 상태(State) 불일치 등의 딥한 장애 상황들을 온몸으로 극복했습니다.
- 가비아 DNS 권한을 AWS Route53으로 위임하며 HTTPS 인프라를 구축하였고, Terraform State Lock과 불량 인증서 강제 교체(Replace) 전략을 통해 무한 대기 현상을 타파했습니다.
- CodeDeploy의 캐싱 원리 파악 및 Flyway를 활용한 무결성 DB 스키마 배포까지, Immutable Infrastructure(불변 인프라)의 진정한 의미를 깨달은 과정입니다.

## 2. 아키텍처 진화 (Architecture Evolution)
1. **모놀리식(Monolithic) 분리**: 블로그 환경과 실습 환경을 분리하고, `Blog_Queue`를 통한 메시지 큐(MSA) 패턴 도입.
2. **Immutable 인프라 도입의 필요성 인지**: 빈 깡통 EC2에 매번 스크립트로 설치(Mutable)하는 방식의 한계(ApplicationStop 에러 등)를 깨닫고 AMI 기반의 불변 인프라 아키텍처로 진화할 토대를 마련.
3. **인프라와 앱 배포의 Lifecycle 철저 분리**: Terraform은 오직 '깡통 뼈대'만, DB 스키마는 Flyway가, 도커 실행 권한은 CodeDeploy가 전담하는 완벽한 책임 분리.

## 3. Deep Dive: 핵심 트러블슈팅
### 💥 DNS 위임과 글로벌 전파 지연 (Taint & Replace)
- **증상**: 가비아에서 AWS Route53으로 네임서버 변경 후, ACM 인증서 검증(DNS Validation)이 30분 이상 지연되며 Terraform 배포가 무한 대기 상태(Hang)에 빠짐.
- **분석**: DNS 전파 시간 지연과 더불어 ACM 서버의 지독한 캐싱.
- **해결**: 멀쩡한 건물 뼈대(Route53)는 두고, 불량 서류(ACM)만 찢어 다시 제출하는 `terraform apply -replace="aws_acm_certificate.cert"` 명령어로 10초 만에 DNS 검증 및 HTTPS 구축 완료.

![DNS 권한 위임 현장](/assets/img/gabia_aws_route53_ns_delegation.png)

![HTTPS 성공](/assets/img/custom_domain_https_success.png)

### 💥 Terraform State 기억상실증과 Import 강제 입양
- **증상**: 강제 종료 후 클라우드에 A 레코드가 존재하나 State 장부에 누락되어 "already exists" 충돌 에러 발생.
- **분석**: Route53과 EC2/ALB의 Lifecycle이 다름. 실무에서는 State Layering(base/app 분리)이 필수.
- **해결**: ClickOps 안티패턴을 피하고, `terraform import`로 실제 AWS 리소스(A 레코드)를 코드의 장부에 안전하게 강제 복구(Sync) 완료.

### 💥 CodeDeploy 에이전트 캐시와 Race Condition
- **증상**: 이전 배포의 불량 스크립트가 실행되거나, `.env`가 생성되기 전에 배포가 질주하여 `grep` 에러 발생.
- **해결**: `/opt/codedeploy-agent/deployment-root`의 악랄한 캐시 구조를 파악하고, 패키지 설치(`init-ec2.sh`)와 배포 권한(`install.sh`)을 철저히 분리. 

![CodeDeploy 성공](/assets/img/codedeploy_success.png)

![CodeDeploy 성공 상세](/assets/img/codedeploy_success_detail.png)

## 4. 파인만 비유 부록 (Feynman Analogy)
어려운 인프라 개념을 초등학생도 이해할 수 있는 비유로 정리합니다.
- **DNS 권한 위임(Delegation)**: 동사무소 직원(가비아)에게 포스트잇 하나 붙이는 게 아니라, 동사무소 소장 자리(트래픽 통제권) 자체를 아예 AWS(Route53)로 통째로 넘기는 아키텍처적 결단.
- **Terraform 4대장**: `variables.tf`(공사 자재), `main.tf`(건축 설계도), `provider.tf`(외주 건설 업체), `outputs.tf`(완공 영수증).
- **CodeDeploy 유령 식당**: 서빙 직원(Agent)도 없는데 본사에서 호출하다가 타임아웃으로 미쳐버려 "옛날 요리 치우다 실패했어!"라고 유령 보고를 던짐.
- **Flyway (깐깐한 금고지기)**: 위험하게 DB를 조작하는 자동 번역기(Hibernate `ddl-auto: update`)와 달리, 개발자가 써준 결재 서류만 1번 읽어 장부에 적고 통과시키는 안전한 금고지기.
- **AWS CLI Broken Pipe**: 정수기 물줄기가 너무 강해 종이컵(페이저)을 끼워 넣었는데, 자동화 서버(무인 공장)에서는 컵이 바로 터지며 압력이 치솟아(Broken Pipe) 발생한 에러.

## 5. Trade-off (기술적 의사결정)
| 결정 사항 | 포기한 것 (Cons) | 얻은 것 (Pros) |
| --- | --- | --- |
| **Blog Queue 패턴 (MSA)** | 모놀리식 단일 폴더의 직관적 관리 | 실습과 블로그 엔진 간의 상태 충돌 방지 및 결합도 제어 |
| **`terraform import` 수동 복구** | 콘솔 삭제(ClickOps)의 빠름과 편리함 | 인프라 코드의 무결성(SSOT) 확보 및 실무형 State 관리 역량 |
| **Flyway 스키마 관리 주입** | Spring Boot의 `ddl-auto: update`의 마법 같은 편리함 | 빈 깡통 인프라 주입 시 테이블 누락 방지 및 DB 배포 안전성 |

## 6. STAR-F Q&A (면접 방어)
**Q. 인프라 코드를 짤 때 Terraform State 충돌이나 지연 문제가 발생한 적 있나요? 어떻게 해결했습니까?**
**A. (Situation)** 가비아에서 AWS로 DNS를 위임하고 ACM 인증서를 발급받는 과정에서 DNS 전파 지연으로 인해 Terraform이 Hang 상태에 빠졌고, 강제 종료 과정에서 `already exists` 충돌이 발생했습니다.
**(Task)** State 락을 해제하고, 캐싱된 인증서를 우회하며, 누락된 상태를 동기화해야 했습니다.
**(Action)** 첫째, 비상 권한으로 `force-unlock`을 수행했습니다. 둘째, ClickOps 삭제를 피하고 `terraform import` 명령을 통해 A 레코드를 State에 안전하게 복구했습니다. 셋째, 멀쩡한 Route53 인프라는 보존하면서 불량 인증서만 `terraform apply -replace` 명령으로 강제 재생성(Taint)하여 10초 만에 DNS 검증을 패스했습니다.
**(Result & Follow-up)** 그 결과 SRE 원칙에 위배되는 수동 개입 없이 100% 코드로 무결성을 회복했으며, Route53(철근)과 ALB(전구)의 라이프사이클 차이를 인지하고 State를 계층적으로 분리(Layering)하는 실무적 인사이트를 얻었습니다.
