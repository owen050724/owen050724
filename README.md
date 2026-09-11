<p align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/profile-header.svg">
    <img src="./assets/profile-header.gif" alt="Yeonoh Park · 박연오 — Security Researcher, SeoulTech CIS Lab" width="100%">
  </picture>
</p>

<p align="center">
  <strong>Vulnerability Research &nbsp; / &nbsp; System Security &nbsp; / &nbsp; Cryptography</strong><br>
  SeoulTech · Cryptography Information Security Laboratory
</p>

<br>

## 01 / About me

I'm **Yeonoh Park (박연오)**, a Computer Engineering undergraduate at **Seoul National University of Science and Technology (SeoulTech)** and an undergraduate researcher at the **Cryptography Information Security Laboratory**.

I study how **identity, authority, and trust** move across software boundaries. My interests span vulnerability research, system security, cryptography, and computer systems, with a focus on whether software enforces the security boundaries it is intended to provide.

Alongside my research, I lead **TCP (Computer Science and Information Technology Club)** and am a member of **STCE (SeoulTech Crypto Engine)**.

<br>

## 02 / Security research

My research covers **authorization boundaries, tenant isolation, credential handling, workflow execution, plugins, and APIs** across open-source projects and coordinated disclosure programs.

<p>
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/research-snapshot-mobile.svg">
    <img src="./assets/research-snapshot.svg" alt="Research record: 5 CVE identifiers, 13 vendor-confirmed outcomes, 92 submitted reports, 40 products and workspaces" width="100%">
  </picture>
</p>

<sub>The 5 CVE identifiers comprise <strong>2 published · 3 reserved</strong>. The 92 reports were submitted from March 22 to August 13, 2026; the 13 vendor-confirmed outcomes include subsequent confirmations and publications.</sub>

### How I work

1. **Model the boundary.** Identify the identities, capabilities, data domains, and trust transitions that define a system's expected security properties.
2. **Follow authority.** Trace how identity and scope propagate between components, looking for changes in how authority is interpreted.
3. **Check the evidence.** Use bounded local validation and competing explanations to distinguish a boundary failure from expected behavior.
4. **Coordinate disclosure.** Separate technical impact from reportability, account for prior work, document limitations, and work with vendors on disclosure.

### Published findings

- **Jenkins · CVE-2026-84677**<br>
  Stored XSS in update-center2, affecting 3.18.3 and earlier and fixed in **3.18.4**. Published September 2, 2026, with **reporter credit**. [Official advisory](https://www.jenkins.io/security/advisory/2026-09-02/).
- **ToolJet · CVE-2026-82872**<br>
  A vendor-accepted authorization boundary vulnerability. The advisory was published August 7, 2026, followed by CVE publication on August 31, with **Finder credit**. [CVE record](https://nvd.nist.gov/vuln/detail/cve-2026-82872).

### Reserved CVEs & coordinated outcomes

- **Dify · CVE-2026-59210** — Accepted; fix shipped since **1.16.0**. CVE reserved; advisory publication pending.
- **Apache DolphinScheduler · CVE-2026-57590 / CVE-2026-66082** — Two separately vendor-confirmed findings with reporter credit. Both CVEs are reserved; severity, remediation, and advisory details remain pending.
- **Grafana** — Accepted report; CVE, remediation, and advisory coordination pending.
- **ToolJet** — A separate report accepted with reporter credit; CVE assignment, remediation, and advisory publication pending.
- **authentik** — Vendor-validated report; fix verification, CVE assignment, advisory publication, and public attribution pending.
- **Five additional coordinated outcomes** — Accepted or otherwise confirmed by their vendors. Product identities and technical details remain private during coordinated disclosure.

<br>

## 03 / Publication

<table>
  <tr>
    <td>
      <p><strong>🏆 GOLD PRIZE &nbsp; / &nbsp; 2026</strong></p>
      <h3>Analysis of Privilege Transfer Vulnerabilities in Messenger-Based Local AI Agents</h3>
      <p lang="ko">메신저 기반 로컬 AI 에이전트의 권한 전이 취약점 분석</p>
      <p>This work examines privilege transfer and authorization boundaries in messenger-based local AI agents.</p>
      <p lang="ko"><strong>Authors</strong><br>박연오 · 최도현 · 김역 · 이창훈 · 손기욱†</p>
      <p><strong>Venue</strong><br>2026 Summer Conference of the Korea Digital Contents Society<br>Undergraduate Paper Competition · July 1–3, 2026</p>
      <p><strong>Recognition</strong><br>Gold Prize in the undergraduate paper competition.</p>
      <p><a href="https://dcs.or.kr/conference/summer2026/notice/article/1086">Conference proceedings and program book</a></p>
    </td>
  </tr>
</table>

<br>

## 04 / Education & honors

### Education

- **Seoul National University of Science and Technology** — B.S. in Computer Engineering, in progress · **2024–present**
- **Busan Science High School** · **2021–2024**

### Honors

- **2026** — Gold Prize, Korea Digital Contents Society Undergraduate Paper Competition, for the paper above.
- **2024** — 12th K-Hackathon finalist; MATLAB Student AI Contest finalist.
- **2023** — Busan SW/AI Education Hackathon **Grand Prize**; Busan Science Exhibition Encouragement Prize.
- **2022** — Busan Future Scientist Award **Grand Prize**; National High School Club SW/AI Contest Encouragement Prize; Busan Science Exhibition Encouragement Prize.

<br>

---

<p align="center">
  <strong>Research collaboration &amp; security inquiries</strong><br>
  Email is the best way to reach me.<br>
  <a href="mailto:24101209@seoultech.ac.kr"><strong>24101209@seoultech.ac.kr</strong></a>
  &nbsp; · &nbsp;
  <a href="https://www.linkedin.com/in/yeonohpark/">LinkedIn</a><br>
  <sub>
    Also on <a href="https://discord.com/users/495616210835079178">Discord</a>
    &nbsp; · &nbsp;
    <a href="https://www.instagram.com/dus_oh24/">Instagram</a>
  </sub>
</p>
