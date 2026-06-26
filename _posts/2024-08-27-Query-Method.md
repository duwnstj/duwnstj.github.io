---
layout: post
title: "Query Method"
date: 2024-08-27T14:48:31.822Z
categories:
  - Tech Log
tags:
  - Spring
---

## Query Method
데이터베이스를 사용하는 애플리케이션 개발에서는 데이터를 어떻게 효율적으로 조회할 것인지가 매우 중요하다. 이 때 자주 사용되는 개념 중 하나가 QUERY Method이다. 이번 글에서는 Query Method가 무엇인지, 왜 사용하는지, 그리고 어떻게 사용하는지에 대해 알아 보겠다.

### 1. Query Method란?
Query Method는 데이터베이스에서 특정 데이터를 조회하기 위한 메서드이다. 특히 ORM 프레임워크에서 많이 사용되며 , 개발자가 SQL 쿼리를 작성하지 않고도 데이터를 손쉽게 조회할 수 있도록 도와준다. Query Method는 메서드 이름을 기반으로 자동으로 SQL 쿼리를 생성하며, 이를 통해 데이터베이스에서 원하는 데이터를 검색할 수 있다.
주로 Spring Data JPA와 같은 Java 기반의 프레임워크에서 많이 사용된다.

### 2. Query Method의 장점
Query Method를 사용하는 장점은 다음과 같다.
- **간결함 : ** 복잡한 SQL 쿼리를 작성할 필요없이, 메서드 이름만으로 데이터를 조회할 수 있다.
- **유지 보수 용이성 : ** SQL 쿼리를 코드에 직접 작성하지 않기 때문에, 코드가 보다 읽기 쉽고 유지보수하기 좋다.
- **자동화된 쿼리 생성 : ** 메서드 이름을 기반으로 ORM 프레임워크가 자동으로 SQL 쿼리를 생성해주므로, 쿼리 작성에 소용되는 시간을 절약할 수 있다.

### 3. Query Method의 기본 사용법
Query Method의 기본 원리는 메서드 이름에 포함된 키워드를 기반으로 쿼리를 생성하는 것이다. 예를 들어 , Spring Data JPA에서는 아래와 같은 방식으로 Query Method를 정의할수 있다. 

```java
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByLastName(String lastName);
}

```text
위의 예제에서 `findByLastName` 메서드는 `lastName`이라는 필드로 사용자를 검색하는 SQL 쿼리를 자동으로 생성한다. `findBy`뒤에 필드 이름을 붙여주는 방식으로 다양한 조건을 설정할 수 있다.

### 4. 다양한 Query Method 사용 예시
Query Method는 단순한 검색 뿐만 아니라, 다양한 조건을 추가하여 복잡한 쿼리도 쉽게 작성할 수 있다.
- **  And 조건** : 여러 필드를 조합하여 검색할 때는 `And`를 사용한다.

```java
List<User> findByFirstNameAndLastName(String firstName, String lastName);

```text
이 메서드는 SQL에서 `where first_name = ? AND last_name = ?`와 같은 쿼리를 생성한다.
이렇게 하면 두조건이 모두 만족하는 데이터를 조회할 수 있다.

- **OR 조건** : 하나 이상의 조건이 맞을 때 데이터를 조회하려면 `Or`를 사용한다. 예를 들어 , 사용자의 이름이나 성 중 하나라도 일치하는 데이터를 찾고자 할 때는 다음과 같은 메서드를 정의할 수 있다.

```java
List<User> findByFirstNameOrLastName(String firstName, String lastName);

```text
이 메서드는 SQL에서 `where first_name = ? or last_name =?`와 같은 쿼리를 생성하며, 둘 중 하나의 조건만 맞아도 데이터를 반환한다.

- **정렬** : 결과를 정렬하고 싶다면 `OrderBy`를 사용한다. 예를 들어, 성을 기준으로 오름차순 정렬하고, 그 내에서 이름을 기준으로 정렬하고자 할 때는 아래와 같이 정의한다.

```java
List<User> findByLastNameOrderByFirstNameAsc(String lastName);

```text
이 메서드는 SQL에서 `where last_name =? order by first_name asc`와 같은 쿼리를 생성한다. `asc`는 오름차순을 의미하며, 내림차순 정렬을 원할 경우 `Desc`를 사용하면 된다.

- **특정 조건** : Query Method는 다양한 조건을 나타내기 위해 여러 키워드를 제공한다. 예를 들어, 나이가 특정 값보다 큰 사용자를 찾고자 할 때는 `GreaterThan` 키워드를 사용한다.
```java
List<User> findByAgeGreaterThan(int age);
```text
이 메서드는 SQL에서 `where age> ? ` 와 같은 쿼리를 생성하며, 주어진 값보다 큰 나이를 가진 사용자만을 반환한다.

- **LIKE 연산자** : 부분 문자열 매칭을 위해 `Like` 키워드를 사용할 수 있다. 예를 들어, 이름에 특정 문자열이 포함된 사용자를 찾고자 할 때는 다음과 같이 정의 할 수 있다.

```java
List<User> findByFirstNameLike(String pattern);

```text
여기서 `pattern`은 SQL의 `Like`절에서 사용하는 `%`와일드 카드를 포함할 수 있다. 예를 들어 , `findByFirstNameLike("%John%")`는 이름에 "John"이 포함된 모든 사용자를 반환한다. 

- **네이밍 전략** :
메서드 이름에 포함되는 키워드 순서가 중요하다. `findBy`,`And`,`Or`,`OrderBy` 등의 키워드를 올바른 순서로 조합하여 원하는 쿼리를 생성해야한다. 순서가 잘못되면 의도하지 않은 쿼리가 생성되거나 오류가 발생할 수 있다.


### 5. Query Method의 한계와 주의 사항
Query Method는 편리하지만 , 모든 쿼리 요구 사항을 처리할 수 있는 것은 아니다. 메서드 이름이 지나치게 길어질 수 있고, 복잡한 비즈니스 로직을 포함한 쿼리를 작성하기에는 한계가 있다. 이러한 경우에는 직접 SQL 쿼리를 작성하거나, `@Query` 애노테이션을 활용하여 커스텀 쿼리를 작성하는 것이 좋다. 
```java
@Query("SELECT u FROM User u WHERE u.age > :age")
List<User> findUsersWithAgeGreaterThan(@Param("age") int age);
```text
### 6. 결론
Query Method는 데이터 조회 작업을 간단하고 효율적으로 처리할 수 있는 강력한 도구이다. 메서드 이름을 기반으로 쿼리를 자동 생성해 주므로, 개발자가 데이터 조회에 집중 할 수 있도록 돕는다. 그러나 복잡한 쿼리나 비즈니스 로직이 포함된 경우에는 쿼리를 직접작성해주거나 하는 대안을 고려하는것이 좋다.

Query Method를 잘 활용하면 개발 생산성을 높일 수 있으며, 보다 유지보수하기 쉬운 코드를 작성할 수 있다.
