# forever-resource-pack

The resource pack for the [Forever](https://github.com/Minecraft-Forever)
Minecraft server. Custom creature models, nothing else.

**This repo is public so that Minecraft can download it.**
`raw.githubusercontent.com` serves a private repo's files only to a
request carrying a token, and the game client has none — a private pack
is a 404 to every player, which on a server with
`require-resource-pack=true` means nobody can log in. There is nothing
sensitive here: it is a few boxes and a PNG.

**It is generated, and it is not edited here.** The source of truth is
`resourcepack/` in the (private) server repo, and
`resourcepack/tools/publish.sh` there builds the zip, pushes it here,
downloads it back to check the hash, and only then points the server at
it. Editing anything in this repo by hand will be overwritten on the
next publish.

```
forever-pack.zip                          what the server serves
pack.mcmeta                               pack format
assets/forever/items/<name>.json          item definition
assets/forever/models/item/<name>.json    geometry
assets/forever/textures/item/<name>.png   skin
tools/build_models.py                     the generator all three come from
```

**It adds nothing but its own namespace.** Everything lives under
`assets/forever/`, so no vanilla mob, block or item changes in any way.
A pack that repainted the piglin brute would have given the server the
same werewolf and changed every brute in every bastion; this does not.

The server points at a **commit** URL, never a branch one —
`raw.githubusercontent.com` caches a branch path for five minutes, so a
player joining just after an update could be handed the previous zip,
whose hash would not match what the server advertises and would
disconnect them.
