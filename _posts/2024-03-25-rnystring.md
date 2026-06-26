---
layout: post
title: "rny_string"
date: 2024-03-25T10:19:38.356Z
categories:
  - Tech Log
tags:
  - 자바
  - 프로그래머스Lv0
---

# 📔문제 설명
![](https://velog.velcdn.com/images/duwnstj12/post/a22c2e36-b18e-4dcc-bf22-6bcaa88412a5/image.png)
***
# 📃입출력 예시
![](https://velog.velcdn.com/images/duwnstj12/post/4cafaab9-807b-4a11-b629-027f03bbf050/image.png)
***
# 📄문제 풀이 코드
```java
class Solution {
    public String solution(String rny_string) {
        String answer = "";
      answer=rny_string.replace("m","rn");
        return answer;
    }
}
```
***
# 문제 풀이
1. `replace()`함수를 이용한다. replace()함수는 문자를 바꾸고 싶을 때 사용한다.
- 사용법 : `string(변수).replace([기존문자],[바꿀문자])` <br>이 문제에서는 rny_string.replace("m","rn")으로 문제를 해결했다.

