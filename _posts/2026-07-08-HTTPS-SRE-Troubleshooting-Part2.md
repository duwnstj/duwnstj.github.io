---
title: "[AWS SRE 대서사시 2/4] DNS 권한 위임과 ACM 전파 지연 트러블슈팅"
date: 2026-07-08 10:00:00
categories: [Tech Log]
tags: [AWS, Terraform, SRE, Troubleshooting, DNS, ACM]
---

# 🚀 AWS SRE 대서사시 2/4: 인프라 뼈대 세우기

> 이 글은 인프라 구축부터 CI/CD 배포까지 이어지는 SRE 트러블슈팅 대서사시의 두 번째 파트입니다.
> - [1/4] Terraform 파괴의 나비효과: VPC 철거 딜레이와 소크라테스 디버깅
> - **[2/4] DNS 권한 위임과 ACM 전파 지연 트러블슈팅** (현재 글)
> - [3/4] Terraform State 기억상실증과 Import 복구기
> - [4/4] 무중단 배포의 덫: GitHub Actions와 CodeDeploy 캐시 트러블슈팅

## 1. 아키텍처 진화 (Architecture Evolution)

### ❌ 과거의 방식 (Mutable & ClickOps)
- 마우스 클릭으로 자원을 생성하고, 에러가 나면 콘솔에서 수동으로 자원을 삭제(ClickOps)하는 안티패턴.
- 인프라 생성(Terraform), 앱 배포(CodeDeploy), DB 스키마 주입(Hibernate ddl-auto)의 책임이 한데 뒤엉켜 있어 어디서 터졌는지 추적하기 힘든 구조.

### 🟢 진화된 방식 (Immutable & MSA Layering)
- **책임의 완벽한 분리(MSA)**: Terraform은 오직 '깡통 뼈대'만 만들고, DB 스키마는 깐깐한 금고지기인 `Flyway`가 검증하며, 도커 실행은 CodeDeploy가 전담합니다.
- **State Layering 인식**: 도메인(Route53)처럼 평생 가는 '철근'과 EC2/ALB처럼 자주 바뀌는 '전구'의 수명 주기(Lifecycle)가 다름을 깨닫고, 이를 Terraform 장부(State)에서 분리해야 한다는 아키텍처적 통찰을 얻었습니다.

## 2. Deep Dive: 치열했던 소크라테스식 문답과 트러블슈팅

### 💥 에피소드 1. 가비아 동사무소와 DNS 권한 위임의 늪
- **상황**: Route53 호스팅 영역을 생성하고 얻은 4개의 NS(네임서버) 주소를 가비아에 등록해야 했습니다.
- **나의 첫 번째 시도**: 가비아의 'DNS 관리' 창에 들어가서 레코드를 추가하려 했습니다.
- **AI의 날카로운 역질문**: *"지금 하신 행동은 가비아 동사무소에 웹사이트 주소 포스트잇을 붙인 것입니다. 우리가 원하는 건 그게 맞나요?"*
- **깨달음**: 아하! 단순히 레코드(포스트잇)를 얹는 게 아니라, 아예 **동사무소 소장 자리(트래픽 통제 주권)** 자체를 AWS Route53으로 이양(위임)해야 한다는 것을 깨달았습니다. 결국 'DNS 설정' 창이 아닌 **'네임서버 설정'** 창으로 찾아가 4개의 주소를 교체함으로써 주권 이양에 성공했습니다!

![DNS 권한 위임 현장](/assets/img/gabia_aws_route53_ns_delegation.png)

### 💥 에피소드 2. 지독한 캐싱과 무한 대기(Hang), 그리고 Taint & Replace
- **상황**: 네임서버를 변경했는데도 Terraform 배포가 `waiting for ACM Certificate` 메시지를 띄우며 30분 넘게 무한 대기(Hang) 상태에 빠졌습니다.
- **나의 추론**: *"너무 오래 걸리는데? 이거 멈춘 거 아니야?"*
- **AI와의 문답**: 전 세계 DNS 우체국에 바뀐 주소록이 복사되는 **'글로벌 전파 지연(Propagation Delay)'** 때문이었습니다. 더 큰 문제는 AWS ACM 서버가 이미 '검증 실패' 상태를 징하게 캐싱(업무 태만)하고 있다는 것이었습니다.
- **해결책 도출**: 잘 지어진 건물 뼈대(Route53)를 헐지 않고, 불량 서류(ACM 인증서)만 찢어서 다시 제출하는 **`terraform apply -replace="aws_acm_certificate.cert"`** 기법을 발동했습니다. 결과는? 10초 만에 DNS 검증 패스!

![HTTPS 성공](/assets/img/custom_domain_https_success.png)

## 3. 파인만 비유 부록
- **DNS 권한 위임 (NS 레코드 변경)**: 동사무소 직원(가비아)에게 "이 주소는 여기야"라고 포스트잇을 적어주는 게 아닙니다. 아예 **동사무소 소장 자리(트래픽 통제권)**를 AWS Route53으로 통째로 위임(이사)하는 웅장한 작업입니다.

## 4. Trade-off (기술적 의사결정)
| 결정 사항 | 포기한 것 (Cons) | 얻은 것 (Pros) |
| --- | --- | --- |
| **`replace`를 통한 강제 갱신** | Terraform이 자동으로 해줄 것이란 막연한 믿음 | 지독한 캐싱에 갇힌 리소스의 Lifecycle을 인간이 강제로 끊어내고 제어하는 통제력 |
