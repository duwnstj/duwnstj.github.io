---
layout: post
title: "⚙️ [트러블슈팅] Spring Boot 멀티모듈에서 bootJar vs plain 착각으로 생긴 문제"
date: 2025-10-16T11:17:42.133Z
categories:
  - Backend
---

## 1️⃣ 사건 개요 — “왜 실행이 안 되지?”

S3에 올린 JAR 파일을 EC2로 복사한 뒤 실행하는 과정에서

다음과 같은 에러가 발생했습니다 👇

```bash
java -jar module-owner-0.0.1-SNAPSHOT-plain.jar
no main manifest attribute, in module-owner-0.0.1-SNAPSHOT-plain.jar

```
처음엔 경로나 자바 버전 문제라고 생각했지만,

결국 원인은 **단순한 설정 차이**였습니다.

> 💡 plain.jar는 실행 가능한 JAR가 아닙니다.
> 

---

## 2️⃣ 원인 — plain vs bootJar의 차이

### 🧩 plain.jar란?

- 단순히 **클래스 파일과 리소스만 담긴 라이브러리 JAR**
- `java -jar`로 실행 불가능
- `Main-Class` 정보가 없어 “no main manifest attribute” 오류 발생

### 🚀 bootJar란?

- **Spring Boot 플러그인**이 만들어주는 **실행 가능한 JAR (Fat JAR)**
- 내부에 `Main-Class`와 의존 라이브러리가 포함됨
- `java -jar` 명령으로 바로 실행 가능

즉,

> bootJar = 시동 걸리는 완성차 🚗
> 
> 
> plain = 부품 상자 🧰
> 

라는 비유가 정확합니다 😎

---

## 3️⃣ 원인 분석 — 잘못된 모듈 설정

문제가 발생한 `module-owner`의 `build.gradle`을 열어보니

다음처럼 되어 있었습니다.

```text
bootJar.enabled = false
jar.enabled = true

```
이건 **실행용 모듈이 아닌 라이브러리 모듈용 설정**입니다.

이 상태에서는 `bootJar` 작업이 비활성화되어,

**실행 가능한 JAR가 아예 생성되지 않습니다.**

---

## 4️⃣ 멀티모듈 프로젝트의 핵심 원칙

Spring Boot 멀티모듈 프로젝트에서는

모든 모듈이 실행용이 아닙니다.

아래처럼 구분해야 합니다 👇

| 구분 | 역할 | bootJar | jar | 실행 여부 |
| --- | --- | --- | --- | --- |
| 실행 모듈 (Application) | 메인 애플리케이션 | ✅ true | ❌ false | ⭕ |
| 라이브러리 모듈 (공통/엔티티 등) | 코드 공유용 | ❌ false | ✅ true | ❌ |

💡 **기억 포인트**

- `bootJar` → 애플리케이션 단위 빌드용
- `jar` → 공통 코드, 엔티티 등 재사용용

---

## 5️⃣ 실행 모듈 설정 

```text
plugins {
    id 'org.springframework.boot'
    id 'io.spring.dependency-management'
}

bootJar {
    enabled = true
}

jar {
    enabled = false
}

dependencies {
    implementation project(':module-common')
    implementation project(':module-entity')
    runtimeOnly 'com.mysql:mysql-connector-j'
}

```
이 상태에서 `./gradlew clean build`를 실행하면

다음과 같은 실행 가능한 JAR가 생성됩니다 👇

```text
build/libs/module-owner-0.0.1-SNAPSHOT.jar

```
이제 정상적으로 실행할 수 있습니다 👇

```bash
java -jar module-owner-0.0.1-SNAPSHOT.jar

```
---

## 6️⃣ 라이브러리 모듈 설정 

라이브러리 모듈은 `@SpringBootApplication`이 없고,

다른 모듈에서 참조되는 형태로 존재합니다.

```text
bootJar {
    enabled = false
}

jar {
    enabled = true
}

```
예시:

- `module-entity`: JPA 엔티티
- `module-common`: DTO, 유틸 클래스 등

이 모듈들은 다음처럼 다른 모듈에서 참조됩니다 👇

```text
implementation project(':module-common')

```
---

## 7️⃣ 실행 모듈이 2개 이상일 때의 배포 전략

제 프로젝트는 `module-owner`(관리자용), `module-user`(사용자용)

**두 개의 애플리케이션 모듈**로 구성되어 있습니다.

💡 포트 충돌을 피하기 위해 각 애플리케이션의 `server.port`를 다르게 설정합니다.

---

## ✅ 정리 한 줄 요약

> 실행해야 하는 모듈 → bootJar=true
> 
> 
> 공통 모듈 → `bootJar=false`
> 

plain JAR는 **`java -jar` 대상이 아닙니다.**

이 원칙만 정확히 구분하면

멀티모듈 빌드나 EC2·Docker 배포에서 더 이상 헤맬 일이 없습니다 💡

---

## ✍️ 마무리

이 문제를 겪고 나서 깨달았습니다.

> “빌드가 성공했다고 끝이 아니구나.”
> 

멀티모듈 환경에서는 각 모듈의 역할을 명확히 구분해야 빌드 산출물도 의도대로 생성되고,배포 시에도 혼란이 없습니다.

이번 경험을 통해

- `bootJar`의 정확한 의미
- 멀티모듈 빌드 관리 방식
- EC2 배포 시 실행 JAR 구분법을 한 번에 정리할 수 있었습니다.