---
layout: post
title: "Spring Security : 전체 흐름과 실제 사용 방법"
date: 2024-12-13T08:12:59.175Z
categories:
  - Backend
tags:
  - Spring
---

Spring Security는 강력한 인증 및 권한 부여 기능을 제공하며, JWT 기반 인증 시스템을 통해 `세션 없는(stateless) 보안`을 구현할 수 있습니다. 
필터 단에서 JWT 토큰을 검증하므로 서버는 `무상태성(Stateless)`을 유지하며, 사용자의 정보를 서버에 저장하지 않는 방식으로 설계됩니다. 
이글에서는 Spring Security의 기본 흐름과 실제 적용하는 방법을 설명하겠습니다.

---

## Spring Security의 기본 흐름
Spring Security는 요청(Request)이 들어올 때부터 `응답(Response)`이 반환될 때까지 다음과 같은 단계로 동작합니다.

![](https://velog.velcdn.com/images/duwnstj12/post/7aaaffab-1e4f-4a6e-a124-2219856256d4/image.png)


### 1. 요청 수신
- 클라이언트가 서버로 HTTP 요청을 보냅니다.

### 2. 필터 체인(Filter Chain)
- 요청은 여러 보안 필터를 거치며 각 필터는 특정 보안 작업(인증,권한 확인)을 수행합니다.
- 정수기 필터 거치듯 설정된 필터를 차례로 거칩니다.

### 3. 인증(Authentication)
- 인증 필터가 사용자의 신원을 확인합니다.
- 인증 성공 시 인증객체(`Authentication`)를 생성하고 `SecurityContextHolder`에 저장합니다.

### 4. 권한 부여(Authorization)
- 인증된 사용자에 대해 요청된 리소스에 접근 권한이 있는지 확인합니다.

### 5. 요청 처리
- 요청이 컨트롤러로 전달되고 비즈니스 로직이 실행됩니다.

### 6. 응답 반환
- 응답이 클라이언트로 반환됩니다. 필요시 보안필터가 응답 데이터를 처리합니다.

---

## 프로젝트에 Spring Security 적용해보기

### JWT Secret Key 생성
먼저 요청에 들어오는 JWT 토큰의 서명을 검증하기 위해 프로젝트 `application.yml` 파일에 jwtSecretKey를 설정해주어야 합니다.

#### application.yml 설정
![](https://velog.velcdn.com/images/duwnstj12/post/a255135a-c612-4189-b1dd-09cbe825a14c/image.png)

**주의사항** : 
- `JWT Secret Key`는 외부에 노출되면 절대 안됩니다.
- 환경변수를 이용해 Git이나 외부에 노출이 되지 않게 관리하는것이 중요합니다.
- 다른사람들이 유추할 수 없게 복잡한 문자열을 `Base64로 인코딩`하여 사용하는 방식을 추천합니다.
---

### Secret Key 초기화
설정된 Secret Key를 사용하여 JWT의 서명을 검증하기 위한 key 객체를 초기화합니다.
![](https://velog.velcdn.com/images/duwnstj12/post/3b65cf7b-c1a6-49e9-a04e-c8bb6c74d756/image.png)

![](https://velog.velcdn.com/images/duwnstj12/post/f2c6a84c-3fba-4b88-8940-305f100eec25/image.png)

- 먼저 encoding된 토큰 값들을 해석하기위해 `인코딩(암호화)`된토큰을 `디코딩(복호화)`합니다. 
- `@PostConstruct`애노테이션은 Bean으로 등록된 후 최초에 한번 실행시키는 애노테이션입니다. 즉, 인코딩된 토큰을 가장 먼저 디코딩(복호화)합니다.

---
### RefreshToken을 사용하는 이유
Refresh Token은 Access Token의 단점을보완하기 위해 사용됩니다. 

#### 1. Access Token의 짧은유효기간
- 보안을 강화하기 위해 `Access Token`의 유효기간을 짧게 설정해야 합니다. 하지만 이 경우 토큰이 금방 만료되므로 사용자가 로그인을 자주 반복해야 하는 불편함이 생길 수 있습니다.
- Refresh Token은 더 긴 유효 기간을 설정해주며 만료된 `Access Token`을 재발급하는데 사용됩니다.

#### 2. 보안 강화
- `Access Token`이 탈취되어도 짧은 유효기간 때문에 피해를 최소화할 수 있습니다.
- `Refresh Token`은 `Access Token`과는 다르게 `DB,캐시(Redis 등)`에서 관리하는 데이터와 비교해 검증을 합니다.
- 따라서 `RefreshToken`이 탈취되었다면 서버에서 해당 Token을 **블랙리스트**로 지정하거나 새로운 Token으로 교체하여 탈취된 Token을 즉시 무효화할 수 있습니다.

---

### JWT 검증 메서드 구현
JWT 토큰의 유효성을 검증하고 클레임(Claims)을 추출하는 메서드를 작성합니다.
![](https://velog.velcdn.com/images/duwnstj12/post/0a505725-b00f-4ef9-8e9c-0aa63f9f2139/image.png)

#### JWT토큰이 만들어지는 방법
- [jwt.io](https://jwt.io/) 사이트에서 확인해보면, JWT 토큰은 다음과 같은 구조로 이루어져 있습니다:

    - Header(타입, 알고리즘)

    - Payload(사용자 정보)

    - Verify Signature(서명)

- 따라서 사용자의 정보를 추출하기 위해 아래와 같은 코드를 사용합니다.

![](https://velog.velcdn.com/images/duwnstj12/post/906db06b-96ca-4fe0-8590-0c9e9bb74d46/image.png)
위 메서드 체이닝 방식은 다음과 같이 해석됩니다

1.디코딩된 `secretkey`(토큰)에서 `.getPayload(사용자)` 정보를 추출할거에요

만약 `Exception`이 발생하면 `catch`를 통해 각 Exception 내용을 알려줄게요 

---

### JWT 필터 
모든 요청에서 JWT를 검증하고 인증 객체를 생성하는 필터를 작성합니다.

{% highlight java %}
@Slf4j(topic = "JwtSecurityFilter")
@RequiredArgsConstructor
@Component
public class JwtSecurityFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String url = request.getRequestURI();

        log.info("url : {}" , url);

        if (Strings.isNotBlank(url) && validateNotPublicUrl(url)) {
            // 나머지 API 요청은 인증 처리 진행
            // 토큰 확인
            String tokenValue = request.getHeader(HttpHeaders.AUTHORIZATION);

            if (Strings.isNotBlank(tokenValue)) { // 토큰이 존재하면 검증 시작
                // 토큰 검증
                String token = jwtUtil.substringToken(tokenValue);

                String type = JwtUtil.ACCESS;
                if (validateRefreshTokenUrl(url)) {
                    type = JwtUtil.REFRESH;
                }

                if (!jwtUtil.validateToken(token , type)) {
                    log.error("인증 실패");
                    response.setContentType(CONTENT_TYPE_JSON);
                    response.sendError(HttpServletResponse.SC_UNAUTHORIZED , "인증에 실패했습니다.");
                    return;
                } else {
                    log.info("토큰 검증 성공");
                    Claims claims = jwtUtil.getUserInfoFromToken(token , type);

                    Long userId = Long.parseLong(claims.getSubject());
                    String email = claims.get(USER_EMAIL, String.class);
                    UserRole userRole = UserRole.of(claims.get(USER_ROLE, String.class));

                    if (userId != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                        AuthUser authUser = new AuthUser(userId, email, userRole);

                        JwtAuthenticationToken authenticationToken = new JwtAuthenticationToken(authUser);
                        authenticationToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                        SecurityContextHolder.getContext().setAuthentication(authenticationToken);
                    }

                }
            } else {
                log.error("토큰이 없습니다.");
                response.setContentType(CONTENT_TYPE_JSON);
                response.sendError(HttpServletResponse.SC_BAD_REQUEST , "토큰이 없습니다.");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }
{% endhighlight %}
- 이 필터에서 `JwtUtil`을 의존성 주입받아 토큰 검증을 실행합니다.
- `filterChain.doFilter(request, response);`를 통해 다음 필터로 요청을 전달합니다.
- `@Order` 애노테이션을 사용하면 필터의 순서를 정할 수 있습니다.
- 필터를 거쳐간 토큰은 인증/권한 처리가 완료된 상태로 서버에 전달됩니다.

---

### 사용자 인증 객체 생성
저희 프로젝트에서는 `JwtAuthenticationToken` 클래스를 사용해 인증 객체를 생성합니다.

{% highlight java %}
public class JwtAuthenticationToken extends AbstractAuthenticationToken {

    private final AuthUser authUser;

    public JwtAuthenticationToken(AuthUser authUser) {
        super(authUser.getAuthorities());
        this.authUser = authUser;
        setAuthenticated(true);
    }

    @Override
    public Object getCredentials() {
        return null;
    }

    @Override
    public Object getPrincipal() {
        return authUser;
    }
}
{% endhighlight %}
- `getCredintials()`메서드는 `null`값으로 설정해줍니다.
    - 그 이유는 jwt 인증을 통해 사용자 정보와 권한 정보를 가져올 수 있기 때문입니다.
- `getPrincipal()` 메서드를 오버라이딩하여 사용자 정보를 반환합니다.
- `authUser` 객체에는 사용자 정보(ID,이메일,권한 등)가 담겨있으며 이를 기반으로 인증 객체가 만들어집니다.
- 이 인증 객체는 Spring Security의 `SecurityContextHolder`에 저장되어 이후 요청에서 인증된 사용자 정보를 참조할 수 있습니다.
---
## 회원가입,로그인 API URL 필터 통과
회원가입이나 로그인 같은 경우는 Token을 인증받기 전이기 때문에 이 API URL은 필터 검증을 통과 시켜주어야합니다.

이 경우는 SpringConfig 파일을 만들어 Security 설정을 추가하면 해결할 수 있습니다.

{% highlight java %}
@Configuration
@RequiredArgsConstructor
@EnableWebSecurity
@EnableMethodSecurity(securedEnabled = true)
public class SecurityConfig {

    private final JwtSecurityFilter jwtSecurityFilter;
    private final CorsConfigurationSource corsConfigurationSource;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
                .csrf(AbstractHttpConfigurer::disable)
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS) // SessionManagementFilter, SecurityContextPersistenceFilter
                )
                .addFilterBefore(jwtSecurityFilter, SecurityContextHolderAwareRequestFilter.class)
                .formLogin(AbstractHttpConfigurer::disable) // UsernamePasswordAuthenticationFilter, DefaultLoginPageGeneratingFilter 비활성화
                .anonymous(AbstractHttpConfigurer::disable) // AnonymousAuthenticationFilter 비활성화
                .httpBasic(AbstractHttpConfigurer::disable) // BasicAuthenticationFilter 비활성화
                .logout(AbstractHttpConfigurer::disable) // LogoutFilter 비활성화
                .authorizeHttpRequests(auth -> auth
                                .requestMatchers("/test").permitAll()
                                .requestMatchers("/api/*/users/login" , "/api/*/users/register").permitAll()
                                .anyRequest().authenticated()
                )
                .cors(c -> c.configurationSource(corsConfigurationSource))
                .build();
    }
}
{% endhighlight %}
- 이 설정 파일에서 `requestMatchers().permitAll()`을 사용하면 특정 URL은 필터 검증을 통과하도록 설정할 수 있습니다.
- 예를 들어, `회원가입(/users/)`과 로그인`(/users/login)` 요청은 필터 검증을 거치지 않고 바로 서버로 전달됩니다.











