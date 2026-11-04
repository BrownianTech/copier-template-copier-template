# CHANGELOG

<!-- version list -->

## v0.28.0 (2026-11-04)

### Features

- Add beta flag to leave Docker out of the GitLab CI tests job
  ([`c92ba86`](https://github.com/cbrown1234/copier-template-copier-template/commit/c92ba868f0edd33a67c5e9490087f02d6d113af1))


## v0.27.2 (2026-11-04)

### Bug Fixes

- Skip the GitLab release job when GITLAB_TOKEN isn't set
  ([`b6aada4`](https://github.com/cbrown1234/copier-template-copier-template/commit/b6aada4c3a49295ccd7a08e41d7394dc634e6b5a))

- Skip the release job in forks
  ([`65b9aae`](https://github.com/cbrown1234/copier-template-copier-template/commit/65b9aaebb47f939a187f76087abd56d8769dffbd))


## v0.27.1 (2026-11-03)

### Build System

- **deps**: Update dependency astral-sh/uv to v0.13.7
  ([#179](https://github.com/cbrown1234/copier-template-copier-template/pull/179),
  [`9cc20a0`](https://github.com/cbrown1234/copier-template-copier-template/commit/9cc20a01559d59c2d59ba08063838628cdfeb6f6))


## v0.27.0 (2026-11-01)

### Features

- Add option to require manual approval before releases
  ([`221419a`](https://github.com/cbrown1234/copier-template-copier-template/commit/221419a3333502a8d4abe51427378bd146930202))


## v0.26.0 (2026-11-01)

### Features

- Add beta flag to run hooks with pre-commit instead of prek
  ([`8369b47`](https://github.com/cbrown1234/copier-template-copier-template/commit/8369b473944fa3336ca66960f081d0a7540ec00e))

- Add Python 3.15 support
  ([`2bbb521`](https://github.com/cbrown1234/copier-template-copier-template/commit/2bbb521efbaf0f09e860ca45a0a58c32075fdfc1))


## v0.25.0 (2026-11-01)

### Features

- Drop Python 3.10 support
  ([`bea40d5`](https://github.com/cbrown1234/copier-template-copier-template/commit/bea40d5d9cdaae3fd9616b1dca5999bf85459b9c))

### Breaking Changes

- Min_python_version no longer offers 3.10. Projects that recorded 3.10 get the new default (3.11)
  on `copier update --defaults`, raising requires-python and ruff's target-version and dropping 3.10
  from the CI matrix.


## v0.24.2 (2026-11-01)

### Bug Fixes

- Ignore ruff's copyright rules in generated templates
  ([`2bc558b`](https://github.com/cbrown1234/copier-template-copier-template/commit/2bc558beeb07c18c0cf0db95b156edbaf1f0c785))


## v0.24.1 (2026-10-31)

### Bug Fixes

- Give the checkout back to root after non-root GitLab tests
  ([`66c02cb`](https://github.com/cbrown1234/copier-template-copier-template/commit/66c02cb6fe2623bd79b6f8e52ca28552079ef59c))


## v0.24.0 (2026-10-31)

### Features

- Add beta flag to run generated GitLab tests as a non-root user
  ([`7aae225`](https://github.com/cbrown1234/copier-template-copier-template/commit/7aae225070c66cf8a0d31d5e76a8f07cd14b3597))


## v0.23.0 (2026-10-31)

### Features

- Add beta GitHub Actions workflow lockfile support
  ([`1eefc52`](https://github.com/cbrown1234/copier-template-copier-template/commit/1eefc5265236bb99644b2b6bdc3f3ccb31b730c7))

### Testing

- Validate the generated renovate.json against Renovate's schema
  ([`abd5b69`](https://github.com/cbrown1234/copier-template-copier-template/commit/abd5b69de7efeb5a0605c30895208ba66d445f8b))


## v0.22.0 (2026-10-31)

### Features

- Use --locked for uv in CI
  ([`4b446ec`](https://github.com/cbrown1234/copier-template-copier-template/commit/4b446ecabf7c60e824dc5067e8a42aaf8e00a9f2))


## v0.21.0 (2026-10-31)

### Features

- **deps**: Update actions/cache action to v6
  ([`7dc42c4`](https://github.com/cbrown1234/copier-template-copier-template/commit/7dc42c4de18e4f9c414c06a5a14f54e70c2492d5))

- **deps**: Update actions/checkout action to v7
  ([`db06ea4`](https://github.com/cbrown1234/copier-template-copier-template/commit/db06ea42f55a15a0136bb9fbdc66c3490c1381c3))

- **deps**: Update astral-sh/setup-uv action to v10
  ([`434945a`](https://github.com/cbrown1234/copier-template-copier-template/commit/434945a404a4c02a24e67b57561e33aa28c23f13))

- **deps**: Update go-task/setup-task action to v2
  ([`9c81601`](https://github.com/cbrown1234/copier-template-copier-template/commit/9c816017711b3d24a51d1bc2dd22c242e53499fc))


## v0.20.0 (2026-10-31)

### Continuous Integration

- Let Renovate update actions in the template's workflows
  ([`2c70c64`](https://github.com/cbrown1234/copier-template-copier-template/commit/2c70c6443452bba393895cb1a1fb3c7b4fb79a55))

- Manage CI tool versions with Renovate annotation presets
  ([`209713a`](https://github.com/cbrown1234/copier-template-copier-template/commit/209713af51efc68c312427d8fb0c51208d627b1d))

### Features

- Give automerged Renovate updates their own PR headroom
  ([`8a7a320`](https://github.com/cbrown1234/copier-template-copier-template/commit/8a7a320b6c8bc2965d708331f5502a0940ea68c4))

- Track and release the versions pinned in the template
  ([`960c3ed`](https://github.com/cbrown1234/copier-template-copier-template/commit/960c3eded7b779816ae6f839495ec38de2c7724c))


## v0.19.0 (2026-10-31)

### Features

- Make python-semantic-release optional
  ([`c5f2b2d`](https://github.com/cbrown1234/copier-template-copier-template/commit/c5f2b2d8371f3db9cb09e43f400f8c5eaf9a6af5))


## v0.18.3 (2026-10-13)

### Bug Fixes

- **deps**: Update dependency copier to v9.19.1
  ([#143](https://github.com/cbrown1234/copier-template-copier-template/pull/143),
  [`1be701e`](https://github.com/cbrown1234/copier-template-copier-template/commit/1be701ee37da3fc306ac26ad27018b8a442aff83))


## v0.18.2 (2026-10-13)

### Bug Fixes

- **deps**: Update dependency copier to v9.19.0
  ([#141](https://github.com/cbrown1234/copier-template-copier-template/pull/141),
  [`51e66c0`](https://github.com/cbrown1234/copier-template-copier-template/commit/51e66c04ae2353ccb7c496c3e962c94776551767))


## v0.18.1 (2026-09-08)

### Bug Fixes

- **deps**: Update dependency copier to v9.18.2
  ([#111](https://github.com/cbrown1234/copier-template-copier-template/pull/111),
  [`ee63ce4`](https://github.com/cbrown1234/copier-template-copier-template/commit/ee63ce4a27d62cec9a4d73600e887fe2c5698132))


## v0.18.0 (2026-09-07)

### Features

- Add self update task
  ([`6b3a591`](https://github.com/cbrown1234/copier-template-copier-template/commit/6b3a591444d760ed9dc384a8f657346ba75a9b4d))


## v0.17.10 (2026-09-07)

### Bug Fixes

- Reduce merge conflicts with template image updates
  ([`c547404`](https://github.com/cbrown1234/copier-template-copier-template/commit/c547404d5249a2245bc43cb3bfc4786b2d81aa8a))


## v0.17.9 (2026-09-07)

### Bug Fixes

- Reduce merge conflicts with template name changes
  ([`4ce2f5e`](https://github.com/cbrown1234/copier-template-copier-template/commit/4ce2f5e18735e454bf1998129b73b09ba673f33a))


## v0.17.8 (2026-09-01)

### Bug Fixes

- **deps**: Update dependency copier to v9.18.1
  ([#104](https://github.com/cbrown1234/copier-template-copier-template/pull/104),
  [`944df18`](https://github.com/cbrown1234/copier-template-copier-template/commit/944df1810661fa0925a8381a0c7729b2813890b0))


## v0.17.7 (2026-08-19)

### Bug Fixes

- **deps**: Update dependency copier to v9.17.2
  ([#90](https://github.com/cbrown1234/copier-template-copier-template/pull/90),
  [`b508bc6`](https://github.com/cbrown1234/copier-template-copier-template/commit/b508bc6c3aefa5bc6e9bdf6b9bb681de4cc61eec))


## v0.17.6 (2026-08-04)

### Bug Fixes

- **deps**: Update dependency copier to v9.17.1
  ([#77](https://github.com/cbrown1234/copier-template-copier-template/pull/77),
  [`bed7f01`](https://github.com/cbrown1234/copier-template-copier-template/commit/bed7f01ccd1f0ad2f1b23bc9af407f72fca3c682))


## v0.17.5 (2026-07-13)

### Bug Fixes

- **deps**: Update dependency copier to v9.17.0
  ([#63](https://github.com/cbrown1234/copier-template-copier-template/pull/63),
  [`ccb3e3b`](https://github.com/cbrown1234/copier-template-copier-template/commit/ccb3e3b9d5aee4a9a06ba6468f272467eac9c924))


## v0.17.4 (2026-07-08)

### Bug Fixes

- Resolve conflicts
  ([`c56bb2a`](https://github.com/cbrown1234/copier-template-copier-template/commit/c56bb2a4e407ecbed94501d5a958b47a926ed0e6))


## v0.17.3 (2026-06-23)

### Bug Fixes

- **deps**: Update copier
  ([#47](https://github.com/cbrown1234/copier-template-copier-template/pull/47),
  [`3a758ea`](https://github.com/cbrown1234/copier-template-copier-template/commit/3a758ea1ca8efb4c0ec111a1d887c666dbd90199))


## v0.17.2 (2026-06-14)

### Bug Fixes

- **deps**: Update copier to v9.15.2
  ([#38](https://github.com/cbrown1234/copier-template-copier-template/pull/38),
  [`265d427`](https://github.com/cbrown1234/copier-template-copier-template/commit/265d4278069ca959dd47920c3f54d3c02087a77d))


## v0.17.1 (2026-05-13)

### Bug Fixes

- **deps**: Update dependency copier to v9.15.1
  ([#18](https://github.com/cbrown1234/copier-template-copier-template/pull/18),
  [`048b1a9`](https://github.com/cbrown1234/copier-template-copier-template/commit/048b1a9ee4fb6da57df7b9c8bdc1640464762b00))


## v0.17.0 (2026-05-03)

### Features

- Switch to open source repo references
  ([`23437ac`](https://github.com/cbrown1234/copier-template-copier-template/commit/23437ac5e2511a1f54c32d4847fbfdd77379a247))


## v0.16.1 (2026-05-03)

### Bug Fixes

- Correct github release uv lock bump
  ([`c38ffc4`](https://github.com/cbrown1234/copier-template-copier-template/commit/c38ffc4b3d50c1749b37ab25bfeec0ffd7d6a9bf))


## v0.16.0 (2026-05-01)

### Features

- Error on undefined vars
  ([`1c6deee`](https://github.com/cbrown1234/copier-template-copier-template/commit/1c6deee1750af3153a525fc0e3605d4ae1db1b70))


## v0.15.1 (2026-04-30)

### Bug Fixes

- **deps**: Update dependency copier to v9.15.0
  ([`6e50bab`](https://github.com/cbrown1234/copier-template-copier-template/commit/6e50babf191992e17d6ffe32206e5076a2d127aa))


## v0.15.0 (2026-04-28)

### Features

- Improve test comments
  ([`33d9a22`](https://github.com/cbrown1234/copier-template-copier-template/commit/33d9a2233b96172d34356d9294955b2116229a7e))


## v0.14.1 (2026-04-22)

### Bug Fixes

- Disable release interup on gitlab
  ([`ca13302`](https://github.com/cbrown1234/copier-template-copier-template/commit/ca13302e614f0e90ded34d320e7c562e220a8407))


## v0.14.0 (2026-04-21)

### Features

- Version alignment
  ([`339e90b`](https://github.com/cbrown1234/copier-template-copier-template/commit/339e90b73ec9acad6daa7b8987b9d4bdea0b170a))


## v0.13.3 (2026-04-20)

### Bug Fixes

- Improve gitlab release ci
  ([`7eff674`](https://github.com/cbrown1234/copier-template-copier-template/commit/7eff6748cb3115dbf3484b34e98407857b79cc81))


## v0.13.2 (2026-04-20)

### Bug Fixes

- Gitlab release needs personal/project token
  ([`4d016cd`](https://github.com/cbrown1234/copier-template-copier-template/commit/4d016cd5732a27a946f1a4da035e856e372c29fd))


## v0.13.1 (2026-04-20)

### Bug Fixes

- Gitlab release needs releases api
  ([`13b28b2`](https://github.com/cbrown1234/copier-template-copier-template/commit/13b28b26f0e0540b4b6c0d8eb0a804b65b61cb03))


## v0.13.0 (2026-04-20)

### Bug Fixes

- Gitlab release needs checkout
  ([`9463862`](https://github.com/cbrown1234/copier-template-copier-template/commit/9463862dc6e153030ec2776f03948ed0a9c083dc))

- **deps**: Update dependency copier to v9.14.2
  ([`7f04dc4`](https://github.com/cbrown1234/copier-template-copier-template/commit/7f04dc4585d1385b8b329cb772c8e67dbcd21c43))

- **deps**: Update dependency copier to v9.14.3
  ([`de6e594`](https://github.com/cbrown1234/copier-template-copier-template/commit/de6e594427c43d5b8cd839ed1982eb7e47c7af87))

### Features

- Add automated release
  ([`68706d5`](https://github.com/cbrown1234/copier-template-copier-template/commit/68706d523832aa230688e0022a1eb052acdf3b65))


## v0.12.1 (2026-04-05)

### Bug Fixes

- Avoid passing release CLI_ARGS to pre-release-checks
  ([`2baa9f0`](https://github.com/cbrown1234/copier-template-copier-template/commit/2baa9f06cf41b3f61b14499d0269d8001d210d0a))

### Documentation

- Add non-interactive usage notes to README for agents and CI
  ([`83f2bcd`](https://github.com/cbrown1234/copier-template-copier-template/commit/83f2bcdd574e99b0731a3efca89753c1dca87c5a))

### Testing

- Assert structured file content instead of raw substrings
  ([`ff50b1f`](https://github.com/cbrown1234/copier-template-copier-template/commit/ff50b1fd6a80759bed038893e6ae8e0a5aac20d3))


## v0.12.0 (2026-04-05)

### Bug Fixes

- **renovate**: Track _min_copier_version in copier.yml.tmpl files
  ([`104f43b`](https://github.com/cbrown1234/copier-template-copier-template/commit/104f43becd5c6b0af37ff70c1273a4dbb9f8f9dd))

### Features

- Add min_python_version question
  ([`0590316`](https://github.com/cbrown1234/copier-template-copier-template/commit/059031604bd23aeee3bc4319a2dd66bc8b0e464d))

- Add sub_project_factory fixture
  ([`05283b5`](https://github.com/cbrown1234/copier-template-copier-template/commit/05283b5a881dbdf4840ac28f024c9a1165c96927))


## v0.11.0 (2026-04-03)

### Features

- Release improvements
  ([`f502070`](https://github.com/cbrown1234/copier-template-copier-template/commit/f502070f0ae35ee1e7960454c0469ac7b5ff4e90))


## v0.10.0 (2026-04-03)

### Bug Fixes

- Unpin docker image
  ([`9131c0b`](https://github.com/cbrown1234/copier-template-copier-template/commit/9131c0ba065c1bc5ff8e950c5f547374371a46e0))

### Features

- Gitlab CI improvements
  ([`af60698`](https://github.com/cbrown1234/copier-template-copier-template/commit/af60698e59f136f79ab3891a5a2c1ea9a20ba56d))


## v0.9.0 (2026-04-03)

### Documentation

- Improve README
  ([`61ec85c`](https://github.com/cbrown1234/copier-template-copier-template/commit/61ec85c0ce8e8766630f6d2693f86d45a8d9df34))

- Improve test harness docs
  ([`237d34f`](https://github.com/cbrown1234/copier-template-copier-template/commit/237d34fbd648fabf7cfebbe31dfaec560dc05cd0))

- Improve test harness docs
  ([`b640632`](https://github.com/cbrown1234/copier-template-copier-template/commit/b640632b0fac6d296ef2b2d45f4c3f1a655a075c))

- Improve test suite docs
  ([`5703801`](https://github.com/cbrown1234/copier-template-copier-template/commit/5703801ecb7311e4b9714915c4b8447336d5c911))

### Features

- Improve template inspection commands
  ([`aa4904d`](https://github.com/cbrown1234/copier-template-copier-template/commit/aa4904d7002436103b0f1a6515519021148a364d))

- Update CI choices
  ([`5733d8f`](https://github.com/cbrown1234/copier-template-copier-template/commit/5733d8fd4e9838267fec8baa0dc94ae8e68ce3e8))


## v0.8.1 (2026-04-01)

### Bug Fixes

- Correct test
  ([`055efbd`](https://github.com/cbrown1234/copier-template-copier-template/commit/055efbd55eed2b40239a19fe7c00880fdab5faac))

### Features

- Add no-default answer handling to tests
  ([`6709473`](https://github.com/cbrown1234/copier-template-copier-template/commit/6709473879569adf77d2d0a27208909a96b11156))


## v0.8.0 (2026-04-01)

### Bug Fixes

- Correct prek usage
  ([`b9fefbb`](https://github.com/cbrown1234/copier-template-copier-template/commit/b9fefbbe35afb1037c2703bf1f8fea93d112cd21))

### Features

- Experimental switch to prek from pre-commit
  ([`a2fb552`](https://github.com/cbrown1234/copier-template-copier-template/commit/a2fb552508795e6bd2c1aad1c11eb52b70321f73))

- Git fetch after release
  ([`193f363`](https://github.com/cbrown1234/copier-template-copier-template/commit/193f363c44fb346f31da2814a0158016a02548f8))


## v0.7.1 (2026-03-31)

### Bug Fixes

- **deps**: Update dependency copier to v9.14.1
  ([`8e14eb0`](https://github.com/cbrown1234/copier-template-copier-template/commit/8e14eb088d2c46adfb8118be7f3e86c2a9b45e5d))

### Features

- Ensure renovate updates copier and _min_copier_version in sync
  ([`dfc4532`](https://github.com/cbrown1234/copier-template-copier-template/commit/dfc453294857ba357c737474165a458d4d94b5d8))

- **repo**: Update copier and _min_copier_version in sync
  ([`64980f7`](https://github.com/cbrown1234/copier-template-copier-template/commit/64980f72602e4f0b3a0967af5d7cee84f9c85541))


## v0.7.0 (2026-03-30)

### Features

- Simplify test helpers
  ([`28d504f`](https://github.com/cbrown1234/copier-template-copier-template/commit/28d504f80df770f72f413da5cf5f0aa97c7a997d))

### Testing

- Check shipped tests pass w/dirty git
  ([`0a3163f`](https://github.com/cbrown1234/copier-template-copier-template/commit/0a3163fc36d71dda569089f110a056364eb5364d))


## v0.6.5 (2026-03-29)

### Features

- Add doc for Copier Template Extensions
  ([`15797aa`](https://github.com/cbrown1234/copier-template-copier-template/commit/15797aa8aa4472f4b084e944c514f4418d0b3702))


## v0.6.4 (2026-03-29)

### Features

- Add asciinema demo to README
  ([`b2b02c8`](https://github.com/cbrown1234/copier-template-copier-template/commit/b2b02c8afd54b013919808b4a533f50f931767ff))

- Add placeholder asciinema demo
  ([`f9593dd`](https://github.com/cbrown1234/copier-template-copier-template/commit/f9593ddc70666a924bb0136d07e04713d008ca3e))

- Add pydantic validated answer example
  ([`18bf8f9`](https://github.com/cbrown1234/copier-template-copier-template/commit/18bf8f965897646ad7d7e79a474cbfebeab15119))


## v0.6.3 (2026-03-29)

### Features

- Add asciinema task
  ([`ab27b39`](https://github.com/cbrown1234/copier-template-copier-template/commit/ab27b3961d7a0a6e94e2cece667a99d663ab6f98))

- Align uv version used in github ci
  ([`d369627`](https://github.com/cbrown1234/copier-template-copier-template/commit/d3696274f2b0a400d9854ddf39af113520f5e2d4))

- Improve docs
  ([`c97bb14`](https://github.com/cbrown1234/copier-template-copier-template/commit/c97bb14c6c566106c49ee490f797b8466858fdec))

- Rename template dir for clarity
  ([`4abe6f1`](https://github.com/cbrown1234/copier-template-copier-template/commit/4abe6f16960888c3ff1c8753f95dff6f01af3923))

- **repo**: Improve cog file updating
  ([`f2cc051`](https://github.com/cbrown1234/copier-template-copier-template/commit/f2cc05155595fdf35a5a4b0913c90c7665a1dd28))


## v0.6.2 (2026-03-24)

### Bug Fixes

- Correct answerfile in README
  ([`95c551a`](https://github.com/cbrown1234/copier-template-copier-template/commit/95c551a86587350ceb1b3fc686165e7f4ac81499))


## v0.6.1 (2026-03-24)

### Bug Fixes

- Correct answerfile in README
  ([`a1457dc`](https://github.com/cbrown1234/copier-template-copier-template/commit/a1457dc55a16c6e645854a25fa0636a3a9d68536))


## v0.6.0 (2026-03-24)

### Bug Fixes

- Exclude chore commits from changelog
  ([`49ccf70`](https://github.com/cbrown1234/copier-template-copier-template/commit/49ccf70de09317cd60bda0f161739239efad246c))

### Features

- Add release:test for local side affects test
  ([`eece162`](https://github.com/cbrown1234/copier-template-copier-template/commit/eece16290817d145d80aa8b25fe845e34efd3699))

- Exclude chore commits from changelog
  ([`106ecf7`](https://github.com/cbrown1234/copier-template-copier-template/commit/106ecf7d00155b78b4cbac04959c76c134200edc))

- Handle semantic release as dev dep
  ([`cd70e33`](https://github.com/cbrown1234/copier-template-copier-template/commit/cd70e338166130d3001343dd70454384fa6befa6))

- Renovate automerges github action digest updates
  ([`12b2de9`](https://github.com/cbrown1234/copier-template-copier-template/commit/12b2de94ccef60aba78bc081e33f3f80199aae41))

- Update readme
  ([`5e45671`](https://github.com/cbrown1234/copier-template-copier-template/commit/5e456718bf240072b30204a846e2adc0c0312292))


## v0.5.8 (2026-02-14)

### Features

- Add plumbum test example
  ([`d028b5e`](https://github.com/cbrown1234/copier-template-copier-template/commit/d028b5ed7c98def369b8fe9801bc60d57517634d))

- **repo**: Add cog setup for updating gitignore
  ([`6f2038e`](https://github.com/cbrown1234/copier-template-copier-template/commit/6f2038ef91477808560f31dc94d032bb4e58356d))

- **repo**: Update cog setup
  ([`0e5f2d3`](https://github.com/cbrown1234/copier-template-copier-template/commit/0e5f2d335b575ce46917a5427b410284bfd8d43f))


## v0.5.7 (2026-02-04)

### Features

- Add gitlab support
  ([`c1bc2cb`](https://github.com/cbrown1234/copier-template-copier-template/commit/c1bc2cb19cfa3ccbe56b0b93bec56d863a4cee3c))

- Add python version matrix testing
  ([`05f7658`](https://github.com/cbrown1234/copier-template-copier-template/commit/05f7658683f827b738e0b38104d8f197080fa0bd))

- Relax python min version
  ([`ea67c3a`](https://github.com/cbrown1234/copier-template-copier-template/commit/ea67c3af8dd23e5072eb68ca5566bd6be2fac6f5))


## v0.5.6 (2026-02-01)

### Bug Fixes

- Remove default copyright name
  ([`d8e4d43`](https://github.com/cbrown1234/copier-template-copier-template/commit/d8e4d435cb0a8534a2aab736ff754c81e9deea30))


## v0.5.5 (2026-02-01)

### Features

- Add license choice
  ([`0f8a655`](https://github.com/cbrown1234/copier-template-copier-template/commit/0f8a655ba8fc16b84395187b076bd7b4ab57ee2c))

- **repo**: Refactor tests
  ([`6c62c75`](https://github.com/cbrown1234/copier-template-copier-template/commit/6c62c75a813845d75b82b34ce11ce062348d375e))


## v0.5.4 (2026-02-01)


## v0.5.3 (2026-01-31)


## v0.5.2 (2026-01-31)

### Features

- Add support for recommended extensions
  ([`b90e69d`](https://github.com/cbrown1234/copier-template-copier-template/commit/b90e69d2d40ff442cf035636ee357939d4669ddd))


## v0.5.1 (2026-01-31)


## v0.5.0 (2026-01-28)

### Features

- Improve ruff config
  ([`903412c`](https://github.com/cbrown1234/copier-template-copier-template/commit/903412cd79dee0103397c96821ba9c22fdff817e))


## v0.4.1 (2026-01-27)

### Bug Fixes

- Correct copier min version bumping
  ([`9d95b4a`](https://github.com/cbrown1234/copier-template-copier-template/commit/9d95b4a9abf121a11ddd2807175d70f9598c080a))


## v0.4.0 (2026-01-25)

### Bug Fixes

- Configure renovate to not pin digests in inner template
  ([`452dd6c`](https://github.com/cbrown1234/copier-template-copier-template/commit/452dd6c5f746f3274d01a5358455f128a257ae74))

- Correct template name for ci files
  ([`3ac003a`](https://github.com/cbrown1234/copier-template-copier-template/commit/3ac003a7ec07bdabeb9facd7193a4b78228cf3eb))

### Features

- Deterministic task version updating
  ([`736d545`](https://github.com/cbrown1234/copier-template-copier-template/commit/736d545a5540d7929fa326a5d47cc17c97329392))


## v0.3.2 (2026-01-25)

### Features

- Add minimal ruff config to template
  ([`c16e5ba`](https://github.com/cbrown1234/copier-template-copier-template/commit/c16e5ba85d873bee067aabe18c18cf39ef82d577))


## v0.3.1 (2026-01-25)

### Bug Fixes

- Correct template name
  ([`9c79d6d`](https://github.com/cbrown1234/copier-template-copier-template/commit/9c79d6d3fe55356216ee38b5dc1f68692bc67ed6))


## v0.3.0 (2026-01-25)

### Features

- Add gitlab ci tests
  ([`1920dcb`](https://github.com/cbrown1234/copier-template-copier-template/commit/1920dcb7783aff4ed6f0045078d4f87e46eb042b))

- Enable autoupdate of min copier version
  ([`e42c732`](https://github.com/cbrown1234/copier-template-copier-template/commit/e42c732150e063a2bb1fde6453d7c5660cf3e0b6))

- Enable choice of template chars
  ([`a8e3a2a`](https://github.com/cbrown1234/copier-template-copier-template/commit/a8e3a2a33e43ddbaa262be307fc2cb96e94d0ae7))

- Enable parametrizing test sub_project fixture answers
  ([`6730c18`](https://github.com/cbrown1234/copier-template-copier-template/commit/6730c1884a76d73fdfcab69b5ee6dafe3e12458d))

- Enable trim_blocks as standard
  ([`58b7382`](https://github.com/cbrown1234/copier-template-copier-template/commit/58b7382521d192b7d67bba246f20e99395260d0b))

- Refactor taskfile
  ([`0ef652a`](https://github.com/cbrown1234/copier-template-copier-template/commit/0ef652a72e709f1e691a93688588ddb2b6fc9712))


## v0.2.0 (2026-01-25)

### Bug Fixes

- Use frozen lockfile for tests
  ([`bdb6ea8`](https://github.com/cbrown1234/copier-template-copier-template/commit/bdb6ea800d029fd65f42959d515e5cec9fb827f4))

### Features

- **repo**: Switch template escape characters
  ([`34e78ac`](https://github.com/cbrown1234/copier-template-copier-template/commit/34e78aca787ddc23b566b4322916a4046607c359))


## v0.1.1 (2026-01-25)

### Bug Fixes

- Update docker example file
  ([`2ae15a3`](https://github.com/cbrown1234/copier-template-copier-template/commit/2ae15a37de135f54db610df6647207009ff74fa8))


## v0.1.0 (2026-01-25)

- Initial Release
