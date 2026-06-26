---
layout: post
title: "[AWS/FinOps] 무작정 배포하다 마주친 5가지 벽과 트러블슈팅 회고 (IAM, SG, OOM, RDS 분리)"
date: 2026-06-24T08:44:32.546Z
categories:
  - Cloud
  - AWS
---


## 🚀 프롤로그: "무지성 따라하기"를 멈추다

AWS EC2에 단순히 스프링 부트 프로젝트를 띄우는 글은 많습니다. 하지만 이번 배포에서는 무작정 콘솔을 클릭하거나 명령어를 복사/붙여넣기 하는 대신, **"왜 이 설정이 필요한가?"** 그리고 **"비용적/보안적 관점에서 최선인가?"**를 끊임없이 질문하며 진행했습니다.

그 과정에서 마주친 5가지 굵직한 문제와 그 해결 과정을 정리해보았습니다.

---

## 🧱 첫 번째 벽: IAM 권한 에러와 '최소 권한의 원칙'

EC2 배포를 위해 CLI로 Key Pair 생성을 시도하자마자 아래와 같은 권한 에러(UnauthorizedOperation)가 발생했습니다.

> `User: arn:aws:iam::...:user/... is not authorized to perform: ec2:CreateKeyPair`
> 

### 💡 원인과 깨달음

원인은 로컬 AWS CLI에 이전 프로젝트에서 사용하던 S3 전용 유저 자격증명이 그대로 남아있었기 때문입니다. 이를 해결하기 위해 `AdministratorAccess` 권한을 가진 유저로 교체하여 문제를 해결했습니다.

하지만 여기서 중요한 보안 원칙을 되짚어보았습니다.
**"CI/CD 파이프라인이나 개발 서버에서 AdministratorAccess를 그대로 쓰는 것이 안전할까?"**
절대 아닙니다. 루트에 버금가는 권한이 깃허브나 외부 서버에 유출되면 계정 전체가 털리게 됩니다. 실무에서는 배포에 필요한 딱 그만큼의 권한만 부여하는 **최소 권한의 원칙(Least Privilege)**을 지켜야 한다는 것을 체감했습니다.

---

## 🧱 두 번째 벽: Security Group (0.0.0.0/0 의 위험성)

EC2가 외부와 통신하려면 방화벽인 Security Group(SG)을 설정해야 합니다. 이때 무심코 22번(SSH)과 80번(HTTP) 포트를 모두 `0.0.0.0/0`(모든 IP 허용)으로 열어두는 실수를 하기 쉽습니다.

### 💡 원인과 깨달음

- **80번 (HTTP):** 외부 사용자가 웹 서비스에 접속해야 하므로 `0.0.0.0/0` 개방이 맞습니다.
- **22번 (SSH):** 서버의 핵심 자원에 접근하는 통로이므로 **내 PC의 IP만** 열어두는 것이 원칙입니다.

나아가 실무의 DB(3306 포트) 설정에서는 특정 IP를 지정하는 것이 아니라, **"웹 서버의 SG를 통과한 요청만 허용"**하는 **SG 참조 패턴**을 통해 아키텍처를 완전히 격리한다는 설계 원칙도 배울 수 있었습니다.

---

## 🧱 세 번째 벽: 멈춰버린 터미널, OOM Killer의 등장

모든 인프라 세팅을 마치고 EC2에서 `docker compose up -d --build`를 실행했습니다. 그런데 Nginx 컨테이너가 `Starting...` 상태에서 멈추더니, SSH 터미널 전체가 먹통(Freeze)이 되며 끊겨버렸습니다.

서버 강제 재부팅 후 `docker ps -a`로 확인해 보니 MySQL 컨테이너가 **`Exited (137)`** 상태였습니다.

### 💡 원인과 FinOps 기반의 해결

137번 에러는 **OOM(Out Of Memory) Killer** 발동을 뜻합니다. 제가 선택한 `t3.micro` 인스턴스의 램은 단 1GB인데, Spring Boot와 MySQL이 동시에 뜨면서 메모리가 한계에 달했고, 커널이 서버 생존을 위해 MySQL을 강제 처형한 것입니다.

과금 없이 문제를 해결하기 위해 하드디스크 공간을 메모리처럼 빌려 쓰는 **Swap 메모리(2GB)**를 적용했습니다.

> 
![](https://velog.velcdn.com/images/duwnstj12/post/11ee8302-3ca1-44a2-b7c3-75eaa9f74890/image.png)

---

## 🧱 네 번째 벽: DB를 외부(RDS)로 분리하라 (Connection Refused)

안정성을 위해 EC2 내부의 MySQL을 외부의 AWS RDS로 분리하는 작업을 진행했습니다. 하지만 배포 직후 Spring Boot 컨테이너가 죽어버렸고, 로그를 부검해보니 아래 에러가 발견되었습니다.

> `Communications link failure`, `Connection refused`
> 

### 💡 원인과 해결

방화벽(Security Group) 문제라면 통상 `Connection timed out`이 뜨지만, `Connection refused`는 주소를 잘못 찾아갔을 확률이 높습니다.
확인 결과, `.env` 파일에 RDS 엔드포인트를 적을 때 `jdbc:mysql:/[주소]` 처럼 **슬래시(/) 하나를 빼먹은 치명적인 오타**가 원인이었습니다. 슬래시를 `//`로 고치자 정상적으로 DB 대문을 열 수 있었습니다.

---

## 🧱 다섯 번째 벽: Unknown Database와 '클라이언트-서버'의 깨달음

문을 열고 들어갔지만 또 다른 에러가 기다리고 있었습니다.

> `Unknown database 'cover_db'`
> 

### 💡 원인과 아키텍처의 분리

AWS CLI로 RDS를 생성할 때 `--db-name` 옵션을 주지 않아, 내부에 `cover_db`라는 스키마(방)가 없는 텅 빈 깡통 상태였던 것입니다.

처음에는 "RDS 안에 들어가서 MySQL을 깔아야 하나?"라고 착각했지만, 클라우드의 핵심인 **클라이언트-서버 아키텍처**를 깨닫고 무릎을 쳤습니다.

1. **서버 (RDS):** AWS가 이미 MySQL을 완벽하게 깔아둔 상태.
2. **클라이언트 (EC2):** 도커를 이용해 일회용 MySQL 접속기(리모컨)를 실행.

```bash
docker run -it --rm mysql:8.0 mysql -h [RDS_엔드포인트] -u root -p
```text
EC2 본체를 더럽히지 않고 1회용 접속기(`--rm`)를 띄워 원격으로 `CREATE DATABASE cover_db;` 명령만 전송한 뒤 리모컨을 부숴버렸습니다.

>![](https://velog.velcdn.com/images/duwnstj12/post/2a22eb9c-ed40-47bd-919a-84327c2dbe55/image.png)

>![](https://velog.velcdn.com/images/duwnstj12/post/5fc4864c-3ac5-4cdf-adfc-7b727056d283/image.png)


---

## 🏁 회고

"단순히 배포에 성공했다"로 끝나는 게 아니라, 에러 메시지를 통해 **권한(IAM), 네트워크 설계(SG), 리소스 비용(FinOps), 그리고 클라이언트-서버 아키텍처**까지 깊이 있게 고민해 볼 수 있는 값진 경험이었습니다. 에러는 두려움의 대상이 아니라, 인프라의 동작 원리를 뼛속까지 이해하게 해주는 최고의 스승이었습니다. 🚀