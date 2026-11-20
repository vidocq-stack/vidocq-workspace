# BUG-20261118-95: the `serialVersionUID` of a woven class — options

Written by FOY with VAUBAN, 2026-11-19. Nobody writes code until Yann picks an option.

## The problem

Vauban weaves a `protected synthetic (ProxyLink)` constructor into a class that needs a client proxy and has no usable
no-arg constructor. The default `serialVersionUID` hashes every non-private constructor (Java Object Serialization
Specification §4.6), so the marker changes it whenever the class is `Serializable` and declares none. Vidocq measured
one library class: -2925986439075262325 before the weaving, 1994005130319834383 after. An object serialized
outside Vauban fails to deserialize under it with `InvalidClassException`, and the reverse fails too.

The lead in `BUG.md` was to have the weaver declare the original value. vauban#351 tried it in every woven class
(commit 4657a3dc) and took it out again, because two jobs downstream failed:

- **Foy `CdiSessionSwapTest`.** A session bean edited under the dev swap now declares a `serialVersionUID`, and its
  value moves with each edit. Foy's `SerialShape` treats a declared value that changed as the developer's word and
  drops the session. With a default value, Foy compares the two shapes and keeps the session.
- **Vidocq `AppLayerDevIT`.** `ClassFingerprint` diffs `target/classes`. It names "changed the ConstantValue attribute
  of field serialVersionUID" as the reload's first change, instead of the method that was added. The pin came from
  the build-tier weaver.

A value taken from the class as it is woven changes with every edit of that class.

## Facts both sessions checked in the code

- **The build tier never weaves a third-party class.**
  - The javac plugin (`WeavePlan`) weaves only the classes of the compilation.
  - `vauban:generate` (`ProxyLinkWeaving`) weaves only the classes the module compiled. It never rewrites a superclass
    from a dependency.
  - `vauban:enhance-dependencies` does not weave.
- **The load-time weaver knows where each class comes from.**
  - `CdiProxifierTransformer` has `ArchiveContext.archivePath()`, which is a jar, an sjar or an exploded directory.
  - The agent (`WeavingTransformer`) has the `ProtectionDomain`, whose `CodeSource` can be null.
- **The dev swap serves the application from a directory.** Both sides of a swap are woven the same way.
- **A class the build tier already wove carries the marker.** `CdiProxifierTransformer` then leaves it alone.

## Options

### A. Pin library classes only (recommended by FOY and VAUBAN)

Only load-time weaving of a class whose archive is a regular file (a jar or an sjar) declares a `serialVersionUID`.
The value is computed from the original bytes, with the §4.6 algorithm that `vidocq:jlink` already uses
(`StagedProxyLinks`). The test is `Files.isRegularFile(archivePath())` in `CdiProxifierTransformer`, and a
`CodeSource` location that is a regular file for the agent. Nothing else is ever pinned:

- a class from an exploded directory;
- a class whose agent location is null or a directory;
- any class woven by the build tier.

- **What it fixes:** the reported case. A library class woven at start keeps the value it has outside Vauban. A
  `vidocq:package` application whose build tier did not run is woven from its jars, and its pin is stable because the
  bytes of a jar do not change between swaps.
- **Foy and Vidocq:** no change. `CdiSessionSwapTest` and `AppLayerDevIT` pass as they are.
- **Cost:** one flag on the weaving path in Vauban. The tests come back from 4657a3dc, including the six §4.6 checks
  against `ObjectStreamClass`.
- **What it leaves:** an application class that Vauban wove has a different default value from the same class built
  without Vauban. That has always been true, and it is documented (see D). The dev swap is unaffected, because both
  sides are woven the same way.

### B. Pin everywhere, as a synthetic field that Foy and Vidocq ignore

The weaver marks the field `ACC_SYNTHETIC`. Foy's `SerialShape` reads a synthetic `serialVersionUID` as undeclared,
and Vidocq's `ClassFingerprint` skips it.

- **Covers:** application classes too.
- **Cost:**
  - companion branches in Vauban, Foy and Vidocq, merged in dependency order;
  - every other tool still sees a declared field: an IDE, a serialization check of another container, a static
    analyser.
  - a value pinned on a class under the dev swap still moves with each edit, so every consumer that compares it must
    know the rule.

### C. A private marker, reached as a nestmate (dropped)

A private constructor is outside §4.6, so the value would not move at all. VAUBAN ruled it out:

- a nest must lie within one runtime package, and the host's `NestMembers` must list the proxy. A proxy generated at
  start comes after its bean class is defined, so the host cannot list it;
- a producer proxy in another package, including the hosted proxies of #351, can never be a nestmate;
- a nested bean already has a host.

It would cover only build-time proxies in the same package, and it would change the `ProxyLink` contract.

### D. No pin in Vauban: document the limit

This is today's state. `vidocq:jlink` pins the classes it stages, and nothing else does. A library class woven at start
keeps the wrong value, which is the reported bug. Under A, D shrinks to the documented remainder: application classes.

## Recommendation

**A, with D's limit documented for application classes.** It is one Vauban PR, it needs no consumer change, and it
fixes the reported case.

`vidocq:jlink` keeps its own `StagedProxyLinks` pin until Vauban publishes the weaver's. Then it calls that one, so
both give the same value.

## Ask

Yann, pick A, B or D. Once you do, VAUBAN writes the Vauban PR, test first. Under A, FOY only switches `StagedProxyLinks`
to the weaver's helper once it is released.
