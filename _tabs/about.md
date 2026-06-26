---
layout: page
title: About
icon: fas fa-info-circle
order: 4
permalink: /about/
---

> **"무작정 서버를 늘리기 전에 아키텍처의 병목을 찾아내고, 클라우드 비용을 통제하는 FinOps / DevOps 엔지니어"**

백엔드의 깊은 동작 원리(JPA, 동시성, 트랜잭션)를 바탕으로, 대규모 트래픽 환경에서 **클라우드 비용을 최적화**하고 **인프라 병목을 해결**하는 데 집중하고 있습니다. 단순한 기능 개발을 넘어, **서버 한 대의 자원 효율을 극대화하는 아키텍처 설계**를 고민합니다.

---

## 🛠️ Tech Stack & Infra

### **[ Cloud & FinOps ]**
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) 
![EC2](https://img.shields.io/badge/Amazon_EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white)
![RDS](https://img.shields.io/badge/Amazon_RDS-527FFF?style=for-the-badge&logo=Amazon%20RDS&logoColor=white)
- **클라우드 아키텍처 구축:** VPC, EC2, RDS, S3를 활용한 고가용성 인프라 설계
- **비용 최적화(FinOps):** 리소스 병목 분석을 통한 인프라 자원 Right-Sizing 및 요금 방어 체계 구축

### **[ DevOps & CI/CD ]**
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
- **자동화:** GitHub Actions를 활용한 무중단 배포(CI/CD) 파이프라인 구축
- **컨테이너:** Docker / Docker Compose를 활용한 일관된 운영 환경 구축 및 네트워크 격리

### **[ Backend & Architecture ]**
![Spring Boot](https://img.shields.io/badge/spring_boot-%236DB33F.svg?style=for-the-badge&logo=springboot&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white)
- **메시지 큐(MQ):** RabbitMQ를 활용한 트래픽 비동기 분산 처리 및 시스템 결합도 완화
- **캐싱 및 동시성 제어:** Redis TTL 및 Redisson 분산 락(Distributed Lock) 적용

---

## 🚀 Projects (Architecture Viewpoint)

### 📚 LibMate (도서관 운영 관리 시스템) | DevOps & Backend

> **목표:** 대규모 도서 리뷰 데이터 조회 최적화 및 알림 시스템의 인프라 병목 해결

* **아키텍처 튜닝 및 비동기 처리 도입 (성능 10배 향상)**
  * [문제] 동기식 API 알림 처리 시 5.14초의 심각한 서버 응답 지연(Timeout) 발생
  * [해결] 무작정 스케일업(Scale-up)으로 클라우드 비용을 낭비하는 대신, **RabbitMQ 기반의 비동기 메시지 큐 시스템**을 도입하여 알림 응답 속도를 **440ms로 단축 (10배 향상)** 및 병목 근본적 해결.
* **DB 부하 분산 및 쿼리 최적화 (성능 52% 개선)**
  * 10만 건 이상의 리뷰 데이터에서 **QueryDSL** 동적 조건 검색 튜닝.
  * 데이터베이스 실행계획(EXPLAIN) 분석 후 인덱스(Index) 튜닝으로 평균 응답 속도 120ms -> 58ms 단축.
* **분산 시스템의 동시성 제어 (무결성 보장)**
  * 다중 인스턴스(Multi-Instance) 환경에서 스케줄러 중복 실행으로 인한 데이터 충돌 발생.
  * **Redis TTL + Redisson 분산 락** 아키텍처를 설계하여 데이터 무결성 100% 보장.
* **운영 안정성 검증**
  * JMeter를 활용한 부하 테스트(Load Test) 수행으로 인프라 한계 수치 검증.

<br>

### 👟 ShoesOrder (신발 주문 관리 시스템) | Backend & Infra

> **목표:** JWT 아키텍처 안정화 및 데이터베이스 병목 분산

* **인증 아키텍처 인메모리 분산**
  * JWT 기반 Access/Refresh 토큰 아키텍처 설계.
  * Redis TTL을 활용하여 인메모리 기반의 즉각적인 로그아웃(세션 무효화) 프로세스 구축으로 DB 부하 방지.
* **장애 대응 및 에러 파이프라인 중앙화**
  * `@ControllerAdvice` 기반 전역 예외 처리 구조를 설계하여 런타임 서버 크래시(Crash) 방어.
* **데이터 조회 최적화**
  * QueryDSL 페이징 처리를 도입하여 대규모 트래픽 유입 시 데이터베이스 I/O 병목 최소화.

<br>

### ✈️ TravelMate (여행 커뮤니티 플랫폼) | Backend

> **목표:** 보안(Security) 기반 백엔드 운영 환경 설계

* **보안 및 접근 제어 아키텍처**
  * Spring Security 체계를 활용한 API 접근 제어망 구축.
* **네트워크 페이로드 최적화**
  * AJAX 비동기 처리를 전면 도입하여 클라이언트-서버 간 불필요한 페이지 렌더링 부하 최소화 및 UX 개선.

---

## 🔥 Troubleshooting Archive (Blog Hub)

단순히 서버의 에러 로그를 지우는 것을 넘어, **"왜 이런 아키텍처를 선택했는지", "비용 측면에서 다른 인프라 대안은 없었는지"** 깊이 있게 회고합니다. (과거에 제가 직접 작성한 트러블슈팅 글들은 좌측 메뉴의 **[Categories](/categories/)** 탭에서 확인하실 수 있습니다!)

* **[DevOps/Infra]** 
  * RabbitMQ 비동기 큐 전환으로 인한 응답 속도 10배 개선 수치 및 아키텍처 트레이드오프 분석
  * Docker Compose 환경 Nginx 리버스 프록시 구축 중 발생한 컨테이너 포트 충돌 및 해결
  * Git 커밋 내 `.env` 민감 정보 유출 1차 방어 및 BFG Repo Cleaner를 활용한 영구 삭제 프로세스
* **[Cloud/FinOps]** 
  * 과금 폭탄 방어: AWS 프리티어 이후 EC2 & RDS 예산 알림(Budget) 설정 및 인프라 최적화
  * AWS VPC 직접 설계: 퍼블릭/프라이빗 서브넷 네트워크 망 분리로 보안 아키텍처 구축
* **[Backend/DB]** 
  * 다중 인스턴스 환경에서 Redis 분산 락(Distributed Lock)을 활용한 스케줄러 동시성 제어 원리
  * 대규모 트래픽 대비: QueryDSL 실행계획 분석 및 B-Tree 인덱스 기반 데이터베이스 병목 해결

---

### 📫 Contact & Channels
- **Email:** duwnstj12@naver.com
- **GitHub:** [https://github.com/duwnstj](https://github.com/duwnstj)
