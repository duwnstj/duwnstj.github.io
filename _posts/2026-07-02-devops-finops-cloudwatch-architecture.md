---
layout: post
title: "[DevOps & FinOps] 무중단 배포부터 CloudWatch 메모리 모니터링까지의 아키텍처 진화기"
date: 2026-07-02 12:18:00 +0900
categories: [DevOps, CI/CD]
tags: [AWS, CloudWatch, FinOps, GitHub Actions, Observability, TroubleShooting]
---

> **바쁜 면접관을 위한 3줄 요약**
> - **문제:** 1GB RAM 프리티어 EC2 환경에서 배포 시 발생하는 OOM 문제와 서버 장애 모니터링의 부재.
> - **해결:** Docker Build 프로세스를 GitHub Actions로 분리하여 EC2 부하를 최소화(FinOps)하고, IAM Role 및 CloudWatch Agent 기반의 메모리 모니터링과 SNS 알람 구축.
> - **결과:** 다운타임 0초의 Blue/Green 무중단 배포를 달성하고, 서버 메모리 임계치 초과 시 Slack으로 실시간 경고를 받는 옵저버빌리티(Observability) 파이프라인 완성.

## 📖 Story: 튜터와의 치열한 문답과 깨달음의 과정

### 1. 첫 번째 오해: 슬랙 알림만 있으면 끝나는 것 아닌가?
기존에 GitHub Actions를 통해 '배포 성공/실패' 슬랙 알림을 구축하고 안심하고 있었습니다. 하지만 "새벽 3시에 접속 폭주로 서버가 죽으면 배포 슬랙 알림이 작동하는가?"라는 압박 질문에 허를 찔렸습니다. CI/CD의 배포 알림과 **운영 중인 서버의 모니터링(Observability)**은 완전히 다른 영역이라는 것을 깨달았습니다.

### 2. 두 번째 위기: CloudWatch는 만능이 아니다?
서버 상태 감시를 위해 AWS CloudWatch를 도입하기로 했습니다. 하지만 CloudWatch는 외부에서 EC2를 감시하므로 **'메모리(RAM)'** 사용량을 기본적으로 알 수 없다는 치명적인 한계를 알게 되었습니다. OOM으로 뻗는 서버를 방어하려면 EC2 내부에 직접 `CloudWatch Agent`를 심어야만 했습니다.

### 3. 세 번째 압박: 에이전트에 어떻게 권한을 줄 것인가?
에이전트가 측정한 데이터를 AWS로 쏘려면 권한이 필요합니다. 처음에는 IAM User를 만들어 Access Key를 `.env`에 넣으려 했습니다. 하지만 이 경우 해커가 EC2를 탈취하면 AWS 제어권을 통째로 뺏겨 막대한 과금(비트코인 채굴 등)을 맞을 수 있는 **FinOps 대참사**가 발생한다는 것을 배웠습니다. 이를 방어하기 위해 비밀번호(Key)가 필요 없는 **IAM Role(역할)**을 EC2에 직접 부여하여 완벽한 보안을 달성했습니다.

### 4. 네 번째 깨달음: 설치는 언제 해야 하는가? (IaC/CaC)
에이전트 설치 명령어를 기존의 `deploy.sh`에 넣으려 했으나, 배포할 때마다 에이전트가 무의미하게 재설치되는 비효율을 깨달았습니다. 서버가 처음 태어날 때(AWS User Data) 딱 한 번만 실행되는 **프로비저닝(`init-ec2.sh`)**과 코드가 바뀔 때마다 실행되는 **배포(`deploy.sh`)**를 명확히 분리하는 데브옵스의 기본 철학을 확립했습니다.

## 🛡️ Self Defense (면접 방어 논리 / Q&A)

**Q. 왜 굳이 메모리 모니터링을 위해 CloudWatch Agent를 추가로 설치했나요?**
A. 프리티어(t2.micro)의 가장 큰 병목은 1GB라는 한정된 RAM에서 발생하는 OOM입니다. AWS 기본 지표는 CPU와 네트워크만 제공하므로, 가장 치명적인 약점인 메모리를 실시간으로 감시하지 못하면 반쪽짜리 모니터링이라고 판단하여 에이전트를 필수적으로 도입했습니다.

**Q. 만약 메모리가 90%를 넘으면 구체적으로 어떻게 슬랙으로 알림이 가나요?**
A. 에이전트가 1분마다 `mem_used_percent`를 CloudWatch로 쏩니다. CloudWatch에는 **Alarm(경보)**가 설정되어 있어, 이 수치가 특정 임계치(예: 80%)를 초과하면 즉시 **SNS(Simple Notification Service)** 토픽을 찌르게 됩니다. SNS는 이 신호를 받아 AWS Chatbot이나 Lambda를 통해 최종적으로 제 슬랙 채널에 경고 메시지를 발송합니다.

**Q. CloudWatch Agent 설정은 수동으로 했나요?**
A. 아닙니다. `cloudwatch-config.json`을 통해 설정(Configuration as Code)을 코드화하였고, `init-ec2.sh`를 AWS User Data에 넣어 서버가 최초 프로비저닝될 때 자동으로 셋업되도록 자동화했습니다.

## 💻 [핵심 코드 스니펫] (Next Session Context용)

### 1. `cloudwatch-config.json`
```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "metrics": {
    "metrics_collected": {
      "mem": { "measurement": ["mem_used_percent"], "metrics_collection_interval": 60 }
    }
  }
}
```

### 2. `init-ec2.sh` (User Data 용도)
```bash
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/home/ubuntu/cover-challenge/cloudwatch-config.json
```
