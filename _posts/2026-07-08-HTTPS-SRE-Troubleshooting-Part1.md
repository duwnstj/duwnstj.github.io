---
title: "[AWS SRE 대서사시 1/3] DNS 권한 위임과 ACM 전파 지연 트러블슈팅"
date: 2026-07-08 10:00:00
categories: [Tech Log]
tags: [AWS, Terraform, SRE, Troubleshooting, DNS, ACM]
---

# 🚀 AWS SRE 대서사시 1/3: 인프라 뼈대 세우기

> 이 글은 인프라 구축부터 CI/CD 배포까지 이어지는 SRE 트러블슈팅 대서사시의 첫 번째 파트입니다.
> - **[1/3] DNS 권한 위임과 ACM 전파 지연 트러블슈팅** (현재 글)
> - [2/3] Terraform State 기억상실증과 Import 복구기
> - [3/3] 무중단 배포의 덫: GitHub Actions와 CodeDeploy 캐시 트러블슈팅

## 1. 10초 요약 (TL;DR)
- 단순한 인프라 세팅을 넘어, **SRE(Site Reliability Engineering)** 관점에서 발생할 수 있는 장애 상황들을 온몸으로 극복한 기록입니다.
- 가비아 DNS 권한을 AWS Route53으로 위임하며 HTTPS 인프라를 구축하였고, 불량 인증서 강제 교체(Replace) 전략을 통해 Terraform의 무한 대기 현상을 타파했습니다.
- 빈 깡통 EC2에 매번 스크립트로 설치(Mutable)하는 방식의 한계를 깨닫고 불변 인프라(Immutable Infrastructure) 아키텍처로 진화할 토대를 마련했습니다.

## 2. 아키텍처 진화 (Architecture Evolution)
1. **모놀리식(Monolithic) 분리**: 블로그 환경과 실습 환경을 분리하고, `Blog_Queue`를 통한 메시지 큐(MSA) 패턴 도입.
2. **인프라와 앱 배포의 Lifecycle 철저 분리**: Terraform은 오직 '깡통 뼈대'만, DB 스키마는 Flyway가, 도커 실행 권한은 CodeDeploy가 전담하는 완벽한 책임 분리.

## 3. Deep Dive: DNS 위임과 글로벌 전파 지연 (Taint & Replace)
본격적으로 HTTPS 환경을 구성하기 위해 가비아의 도메인 네임서버를 AWS Route53으로 위임했습니다. 

![DNS 권한 위임 현장](/assets/img/gabia_aws_route53_ns_delegation.png)
*가비아 네임서버를 AWS Route53의 네임서버 4개로 완벽히 위임한 현장*

하지만 순탄치만은 않았습니다.

### 💥 트러블슈팅 상황
- **증상**: 가비아에서 AWS Route53으로 네임서버 변경 후, ACM 인증서 검증(DNS Validation)이 30분 이상 지연되며 Terraform 배포가 무한 대기 상태(Hang)에 빠졌습니다.
- **분석**: DNS 전파 시간 지연과 더불어 ACM 서버의 지독한 캐싱이 원인이었습니다. 이미 꼬여버린 인증서 발급 요청은 네임서버가 뒤늦게 전파되어도 승인되지 않고 허공을 떠돌았습니다.
- **해결**: 멀쩡한 건물 뼈대(Route53)는 두고, 불량 서류(ACM)만 찢어 다시 제출하기로 결단했습니다. `terraform apply -replace="aws_acm_certificate.cert"` 명령어로 인증서 리소스만 강제 재생성(Taint)하여 10초 만에 DNS 검증 및 HTTPS 구축을 완료했습니다.

![HTTPS 성공](/assets/img/custom_domain_https_success.png)
*우여곡절 끝에 성공적으로 자물쇠(HTTPS)가 채워진 도메인 연결 화면*

## 4. 파인만 비유 부록 (Feynman Analogy)
어려운 인프라 개념을 초등학생도 이해할 수 있는 비유로 정리해 보았습니다.
- **DNS 권한 위임(Delegation)**: 동사무소 직원(가비아)에게 "이 주소록 좀 갱신해 줘"라고 포스트잇 하나 붙이는 게 아니라, 동사무소 소장 자리(트래픽 통제권) 자체를 아예 AWS(Route53)로 통째로 넘기는 아키텍처적 결단입니다.

> **다음 편 예고**: DNS 지연 때문에 Terraform 배포를 강제 종료했더니, 클라우드에는 자원이 생성되었지만 로컬 State 장부에는 기록되지 않는 대참사가 벌어집니다. 2편에서는 이를 수동으로 복구하는 `terraform import` 구출 작전을 다룹니다! 👉 **[2편으로 이어짐]**
