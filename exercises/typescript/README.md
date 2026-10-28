# TypeScript

Exercises for the [TypeScript Basics](https://espinovah.github.io/project-mimir/#/lessons/core/typescript-basics) lesson: typing functions and objects, unions and narrowing, generics, and checking untyped JSON from an API before you trust it. Do the [JavaScript](../javascript/) set first.

## How to run

You need Node 22.18 or newer (`node --version`). There's nothing to install: Node runs `.ts` files by stripping the types, and the tests use Node's built-in test runner.

```bash
cd exercises
npm test -- typescript/01_typed_functions   # one exercise
npm test -- typescript                      # the whole set
```

Stripping types means the tests check what your code **does**, not whether your types are right. Let your editor check the types as you go (VS Code does this out of the box), or run the compiler on a file:

```bash
npx -p typescript tsc --noEmit --strict --target es2022 --module nodenext --allowImportingTsExtensions typescript/01_typed_functions/typed_functions.ts
```

Each exercise folder has a `README.md` with the task, a starter file to edit, a test file, and a reference solution in `solution/`.

## Exercises

| # | Exercise | Practices |
| --- | --- | --- |
| 01 | [Typing functions and objects](01_typed_functions/) | parameter and return types, `interface`, literal unions, optional parameters |
| 02 | [Unions and narrowing](02_unions_narrowing/) | discriminated unions, `switch` narrowing, exhaustive `never` checks, `typeof` and `Array.isArray` |
| 03 | [Generic helpers](03_generics/) | type parameters, `extends` constraints, `Record`, a `Result<T>` type |
| 04 | [Validating an API response](04_validate_response/) | `unknown`, type guards, turning raw JSON into a typed object with path-based errors |
