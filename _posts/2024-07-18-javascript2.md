---
layout: single
title: "JavaScript의 변수"
categories: [JavaScript]
tag: [JavaScript]
author_profile: false
sidebar:
  nav: "docs"
last_modified_at: 2024-07-18
---

> ## JavaScript의 변수

- 변수란 데이터가 저장될 수 있는 공간을 말한다.
- 변수의 이름을 정하는 규칙이 있는데 변수는 직관적이고 , 변수에 저장되는 값과 관계되는 이름으로 정해야한다.
- 데이터가 저장되는 공간의 메모리 주소 대신 변수의 이름으로 해당 공간을 가리킬 수 있다.

## let 키워드

- 자바스크립트에서 `let` 키워드를 사용하여 변수를 선언할 수 있다.

  ```javascript
  let name;
  console.log(name);
  ```

  ```javascript
  // 결과
  undefined;
  ```

  - **변수 name을 선언하면 name이란 이름을 가진 메모리 공간이 생성된다.**
  - 지금 이와같은 결과가 나오는 이유는 변수를 선언하고 값을 할당하지 않아서이다. 이 결과로 `undefined`가 나오게 된다.
  - `undefined`는 변수는 존재하나, 어떠한 값으로도 할당되지 않아 자료형이 정해지지(undefined) 않은 상태이다.

## 변수 초기화 및 재할당

- 변수에 값을 할당할 때는 변수명과 값을 `등호(=)`로 연결한다.
- 변수에 이미 값이 선언되어 있어도 새로운 값을 재선언할 수 있다.

```javascript
let name; // 변수 선언
name = "홍길동"; // 변수 초기화
name = "신사임당"; // 변수 재할당
console.log(name);
```

```javascript
// 결과
신사임당;
```

- 결과로 신사임당이 나오게 된다.
- **변수에 저장되었던 값을 다시 재할당을 하게 되면 그 값이 다시 name변수에 저장이된다.**

- 또한 변수 선언과 초기화를 동시에 진행 할 수 있다.

```javascript
let name = "홍길동";
console.log(name);
```

```javascript
// 결과
홍길동;
```

## const

- 자바스크립트에서 상수는 `const`키워드를 사용하여 선언한다.
- 상수란? `변하지 않는 값`을 말한다.
- 한번 선언되면 다시 선언되거나 새 값을 대입할 수 없다.

```javascript
const movieName = "홍길동";
console.log(movieName);

//결과
홍길동;
```

- <span style="color : red;">const를 사용할 때 주의 할점이 있다.<span>
- const는 let과 달리 선언과 동시에 값을 할당하지 않으면 오류가 발생하게 된다.

```javascript
const movieName;

// 결과

Uncaught SyntaxError: Missing initializer
in const declaration
// 이러한 에러가 뜬다.
```

- **const 키워드로 선언된 변수의 값을 변경하면 TypeError가 발생한다.**

```javascript
const movieName = "홍길동";
movieName = "범죄도시";

// 결과
VM34:2 Uncaught TypeError: Assignment to constant variable.
//이러한 에러가 뜨게 된다.
```

## 자바와 자바스크립트의 변수 차이점

자바에서는 `int,double,String` 이런식으로 `자료형 타입`이 있지만,<br>
자바 스크립트는 이러한 자료형이 없이 `let`을 선언해주면<br> 자바스크립트가 자동으로 정수는 정수로 저장해주고<br> 문자는 문자로 저장해준다.<br>

## 변수 명명 규칙

- 변수명은 간결하고 그 용도가 명확하게 나타나야한다.
- 추상적이고 모호한 이름이라면 협업할 때 다른 개발자들이 이해하기 힘들다. 따라서 암묵적으로 `변수명은 명확해야한다는 개발자 룰이 있다.`
- 문자와 숫자, 특수문자는 $와\_만 사용할 수 있다.
- 첫글자는 숫자가 될 수 없다.

```javascript
let $salary;
let _jobTitle;
```

> ### 카멜 표기법(camelCase)

- 변수명은 전체적으로 소문자를 사용하지만, 연결 단어의 첫 글자는 대문자로 작성한다.
- 이렇게 사용하면 변수명의 가독성이 훨씬 좋아진다.

```javascript
let customerId;
let phoneNumber;
```

### 예약어 사용 불가

- 자바스크립트의 예약어는 변수명으로 사용할 수 없다.
- 예약어란? `문법적인 의미를 가지는 단어이다.`
- 대표적으로 `let,if,for,while,switch`등이 있다.

```javascript
let if;

// 결과
Uncaught SyntaxError : Unexpected token 'if'
// 이러한 오류가 뜨게 된다.
```

> ## 주석

- 주석은 나중에 다시 코드를 보더라도 이해가 될 수 있게 상세하게 적어준다.
- <span style="color:red;">항상 주석을 다는 습관을 들이자</span>
- 코드에 설명을 추가할 때 사용한다.
- 나중에 코드를 다른 사람이 보게 될때 주석이 쉽게 이해할 수 있도록 도와준다.
- **코드의 실행에 영향을 주지 않으며 브라우저가 코드로 인식하지않는다**
- 자바스크립트는 `한줄 주석,여러줄 주석` 두가지 주석 기호를 가지고 있다.
- 한줄 주석을 작성할 때는 `//` 기호를 사용한다.

```javascript
// 이런식으로 한줄 주석을 작성한다.
```

- 여러 줄의 주석을 작성할 때는 `/**/` 기호를 사용해서 감싸주면 된다.

```javascript
/* 해당 부호로 감싸면 이런식으로 여러 줄의 주석을 작성할 수 있다 */
```

> ## 세미콜론으로 문장 구분하기

- 문장의 끝을 나타내기 위해 `세미콜론(;)`을 사용한다.
- 자바에서는 세미콜론으로 코드를 끝맺음 하지 않으면 에러가 나지만, 자바 스크립트에서는 세미콜론을 사용하지 않아도 에러가 나지않는다.
- **하지만 대부분의 프로그래밍 언어가 세미콜론으로 닫아주기 때문에 닫아주는것을 권장한다.**

```javascript
let example = "세미콜론이 있는 버전";
let example2 = "세미콜론이 없는 버전";
```

> ## 들여쓰기

- 들여쓰기는 코드의 가독성을 높여주는 중요한 요소이다.
- 들여쓰기를 사용하면 코드의 구조와 포함 관계를 명확하게 보여줄 수 있다.

```javascript
function indentTwo() {
  console.log("two");
}

function indentThree() {
  console.log("Three");
}

//결과
two;
three;
```

<hr>

출처 : [자바스크립트(코딩밸리)](https://www.codingvalley.com/)의 강의를 토대로 만들었습니다.
