# Writing a build compatible extension for a Vidocq brick

A brick's CDI integration is often a `BuildCompatibleExtension`: Ravel's synthesises the `@ConfigProperty` beans,
Cassini's gives a scope to the `@Path` classes, Dirac's lists the classes that carry metrics. This page says how to
write one so that it works at build and the application starts without running it. It is for whoever implements a
new specification, human or agent.

Reference pages: Vauban, `concepts.adoc`, "Extensions frozen at build" and "Writing an extension the build can
freeze"; Vidocq, `internals.adoc`, "Build compatible extensions, frozen at build".

## What happens to an extension

1. **While the application compiles**, the Vauban annotation processor runs the extensions it finds on the processor
   path, on the classes being compiled. Those classes cannot be loaded yet.
2. **After compilation**, `vidocq:generate` runs every extension of the application once more, on the path the
   application starts with, the classes loadable this time. It writes what they did in the application's output
   (`META-INF/vauban-frozen-extensions.properties` and two companion files). This is the *freeze* (Vidocq/vauban#288).
3. **At start**, the container loads that record instead of running the extensions, when its deployment is the one
   frozen. Otherwise it runs them, as it always did: under `vidocq:dev`, on a test class path, in a TCK deployment,
   on Weld or Open Liberty.

So an extension runs in three places, and in the packaged application it does not run at all. Whatever it must do
at start cannot live in its phases.

## The rules

1. **Compute from the classes of the deployment only.** No configuration value, environment variable, file outside
   the application or network resource in a phase: at build they are the build machine's.
2. **Check the start environment in an observer of `jakarta.enterprise.event.Startup`.** Collect at build what must
   be checked, hand it over as parameters, check when `Startup` fires, and throw a
   `jakarta.enterprise.inject.spi.DeploymentException` listing every problem: the container start fails with that
   exception. Two shapes, both in production:
   - a synthetic observer with parameters, when the check needs what the extension collected
     (`ravel-cdi-vauban`, `ConfigStartCheck`):

     ```java
     // ConfigCdiExtension, at @Synthesis: nothing is registered when there is nothing to check
     components.addObserver(Startup.class)
             .priority(ConfigStartCheck.PRIORITY)
             .withParam(ConfigStartCheck.PROPERTY_KEYS, column(requiredProperties, RequiredProperty::key))
             .withParam(ConfigStartCheck.PROPERTY_TYPES, column(requiredProperties, RequiredProperty::type))
             .withParam(ConfigStartCheck.PROPERTY_DEFAULTS, column(requiredProperties, RequiredProperty::defaultValue))
             .withParam(ConfigStartCheck.PROPERTY_SITES, column(requiredProperties, RequiredProperty::site))
             .observeWith(ConfigStartCheck.class);
     ```

     Each column is a `String[]`; the types travel by class name and are loaded at start, the site is the text the
     message prints (`Class#field`).
   - a plain bean with an observer method, when the check needs nothing from the extension
     (`cervantes-cdi-vauban`, `JwtConfigurationCheck`): it is in the brick's bean archive, so it also runs on a
     container that never ran the extension.

   Give the observer an early priority, so that no application observer works for an application that will not
   start.
3. **Add annotations, never remove them.** `ClassConfig.addAnnotation` is frozen; `removeAnnotation` is not, and one
   removal sends the whole deployment back to running its extensions at start.
4. **Carry data in parameters, not in fields.** `withParam` takes primitives, `String`, `Class`, enums, annotations,
   `ClassInfo`, `AnnotationInfo`, `InvokerInfo` and their arrays; they reach the creator or the observer at start. A
   field of the extension does not: no extension instance exists at start.
5. **Do not load an application class during compilation.** `Class.forName` fails in the processor; read the language
   model instead, or accept that the result is completed by the freeze after compilation (Dirac's list of metric
   classes was empty at compile time and is complete in the freeze).
6. **Ask `ExtensionPhase.isBuildTime()` only as a last resort.** An extension that asks is taken to have left work
   for the start, and runs again at each start. If one phase cannot avoid the start environment, put it in a class of
   its own, so that the rest stays frozen (Heisenberg's `InterceptorPriorityExtension`).

## On the Vidocq side

- The Vidocq extension has a `-codegen` bundle that brings the brick's extension to the processor path
  (`vidocq-runtime-<x>-extension-codegen`: the brick's `*-cdi` jar, the CDI API, what those jars leave `provided`),
  declared in the extension descriptor (`codegen = ...`), the BOM, the root `dependencyManagement` and the regenerated
  catalog. Without it the compilation does not see the extension, and nothing it adds reaches the code generated
  while compiling (Vidocq/vidocq#546).
- A bean the Vidocq extension adds in `beforeStart` goes through `VaubanContainerBuilder.addHostBean(type, factory)`:
  a holder that exists or not with the configuration of the start must leave the record valid.
- A TCK or integration harness that lists a brick's beans one by one must list the start check too
  (`cervantes-tck`, Vidocq's `CervantesJwtIntegrationTest`).

## Other containers

The same extension runs on Weld and Open Liberty, at deployment. Two things met so far:

- Arquillian's embedded Weld fires no `Startup` event: Ravel's portable extension takes the synthetic observer over
  and runs it at `AfterDeploymentValidation`.
- Keep `io.vidocq.vauban.api` optional (`requires static`) and tolerate its absence where the extension asks
  `ExtensionPhase`, as Ravel's `runsAtBuildTime()` does.

## Tests

- Red first: the check alone, fed with the collected data and without the extension, fails and passes as expected.
- A container that runs the extension, and one built from a frozen deployment
  (`VaubanContainerBuilder.freezeExtensions(output)`, then a builder whose class loader sees `output`): the same
  beans, and `container.extensionsAtStart().ranAtStart()` empty.
- In a Vidocq application: the `layer` section of the startup report says `cdi extensions  N extensions frozen at
  build`; the application behaves the same with `-Dvidocq.freezeExtensions=false`; a missing value still stops the
  start in both.
- The brick's TCK, unchanged, since a TCK deployment runs the extensions at start.

## Checklist for a new brick

- [ ] No phase reads the start environment; `git grep ExtensionPhase` finds nothing, or one small class.
- [ ] Start checks are `Startup` observers that throw `DeploymentException`.
- [ ] No `removeAnnotation`.
- [ ] A `-codegen` bundle brings the extension to the processor path; `checkpom` agrees.
- [ ] Beans added by the Vidocq extension use `addHostBean`.
- [ ] The build prints `Vauban: froze N build compatible extension(s)` with no extension left for the start, and the
      startup report says so.
- [ ] Weld and Open Liberty modules green, TCK count unchanged.
