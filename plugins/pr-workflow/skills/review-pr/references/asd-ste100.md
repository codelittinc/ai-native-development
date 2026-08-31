# How to write review feedback in ASD-STE100

Write all review feedback in ASD-STE100 Simplified Technical English. This applies to the
terminal summary and to every pull request comment. Simplified Technical English makes technical
writing clear and unambiguous for each reader, and specially for a reader whose first language is
not English.

Apply these rules to the prose that you write. Do **not** change the code of the user, quoted log
output, or an identifier to obey these rules. Simplified Technical English controls your
sentences. It does not control the code.

## The writing rules

1. **Give one instruction in one sentence.** Divide a request that has two parts.
   - Incorrect: "Extract the query into a helper and add a test so the logic is covered."
   - Correct: "Extract the query into a helper. Add a test for the helper."

2. **Keep the sentences short.** Use 20 words or fewer for an instruction. Use 25 words or fewer for a descriptive sentence.

3. **Use the active voice.** Name the thing that does the action.
   - Incorrect: "The lock should be acquired before the write."
   - Correct: "Acquire the lock before the write."

4. **Use the imperative for an instruction.** Start a necessary change with a verb.
   - Correct: "Add a null check." "Move this call into the transaction."

5. **Use the simple present tense or the simple past tense.** Do not use a perfect tense or a future tense when a simple tense is sufficient. Do not use an `-ing` form as the main verb.
   - Incorrect: "This is going to cause a race condition."
   - Correct: "This causes a race condition."

6. **Use simple words.** Use the short common word, not the long word.
   - Use `use`, not `utilize`. Use `about`, not `regarding`. Use `start`, not `initiate`. Use `end`, not `terminate`. Use `enough`, not `sufficient`. Use `make sure`, not `ensure`. Use `fix`, not `remediate`. Use `also`, not `additionally`.

7. **Use one word for one thing.** Do not use a synonym for a concept that you named already. If you write "function", do not call the same thing a "method" or a "routine" later.

8. **Use the articles `a`, `an`, and `the`.** Do not remove them to make the text shorter.
   - Incorrect: "Add check to handler."
   - Correct: "Add a check to the handler."

9. **Write a positive statement.** Tell the reader what to do. Do not tell the reader only what to avoid.
   - Incorrect: "Do not forget to close the connection."
   - Correct: "Close the connection after the write."

10. **Do not use slang, an idiom, jargon, or humor.** Write "this fails when the input is empty", not "this blows up on empty input".

11. **Do not use a pronoun that is unclear.** Write the noun again if "it", "this", or "they" can point to more than one thing.
    - Incorrect: "It calls the API and it can be null."
    - Correct: "The handler calls the API. The API response can be null."

12. **Give a reason with each finding.** State the problem. Then state the effect.
    - Correct: "This query has no index. The report is slow for a large data set."

## The shape of a finding

Write each finding in this order, in short sentences:

1. **What** — the problem, in one sentence.
2. **Why** — the effect or the risk, in one sentence.
3. **Fix** — the action, as an imperative.

An example finding:

> **Security — the authorization check is missing.**
> This route reads a customer record. The route does not check the tenant of the caller.
> A user can read a record that belongs to a different tenant.
> Add a tenant check before the query.

## The check before you send the review

- Does each sentence have 20 words or fewer?
- Does each sentence give one idea?
- Is the voice active and the tense simple?
- Did you use one word for each concept?
- Did you give the reason for each finding?
