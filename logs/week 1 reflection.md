Fri, Mar 6, 2026 2:02am
*I wrote this without AI*

I want to write a reflection about this week's progress on passagemath. I only learned that passagemath/sage even existed 72 hours ago. I relied very heavily on AI assistance for all of my contributions and have been feeling inadequate. trying to think what I should reflect on. our work this week:
- [#6](https://github.com/passagemath/passagemath-pkg-numerical-interactive-mip/pull/6): the one that started it all. 12am: remembered my friend said there could be structured research opportunities on mathlab already and it could be an easier place to get started than emailing professors. passagemath seemed most relevant to my interests in simulation, modeling, and optimization. TURNED OUT APPLICATIONS WERE ALREADY CLOSED! so I decided to write a PR to compensate.
- [#2237](https://github.com/passagemath/passagemath/pull/2237): this was a big one. we learned about [m4](https://github.com/passagemath/passagemath/blob/3373b0ee076cd5b05560ffb48af204164438df29/m4/sage_python_package_check.m4#L4) files. it was causing linux builds to crash
- [#2239](https://github.com/passagemath/passagemath/issues/2239): also a big one too. comment on [checking logs](https://github.com/passagemath/passagemath/pull/2237#issuecomment-3998882600) led us to feed [mingw-logs-windows-2022-standard-sitepackages](https://github.com/sacchen/passagemath/actions/runs/22657762491/job/65671085474#step:12:22) into gemini and it discovered why windows CIs were failing!
- [#2243](https://github.com/passagemath/passagemath/issues/2243): this one was funny because I thought I would just try out the combinatorics package using uv just to see what it's like as an user. immediately found a bug within 5min of using it. I was going to sleep at 12am but ended up writing an issue until almost 4am.
- generally noticing an interesting pattern of infra build problems and issues directly from modularization.

Feeling inadequate from AI use:
- AI was used for scoping out problems, prioritizing problems, explaining bugs and fixes to me, writing the actual fix, checking the fix, writing the PR, writing the comments
- Makes me feel like I'm just a monkey hitting "accept permissions" and copying and pasting.
- Well hey #2237 and #2239 were going unfixed until silly monkey me made the AI do it.
- The positive view on this is I am injecting my taste on things. I'm choosing where to direct work. I set the style of Simon Willison and only working on high leverage things.
- It's very easy to compare myself to friends who write from scratch and debug/trace way better than me. There's also the flip side of THIS TOOL IS RIGHT HERE! there are bugs going unfixed! there is so much to learn! 
- I think it's probably the best time in the world to be doing this stuff. I'm getting a lot of exposure to code, going thru a codebase, generally spending a lot of time thinking about what's going on. I think that's the main positive thing.

I think mkoeppe's comments were very helpful. concise, direct style, and gave me lots of stuff to explore and dig into. generally impressed with speed and layers he's familiar with.
- I didn't know there was a [whole layer underneath](https://github.com/passagemath/passagemath/pull/2237#issuecomment-3994966784) with CI builds. also they take way too darn long. [CI MinGW #2](https://github.com/sacchen/passagemath/actions/runs/22657762491) took 6 hrs!! google could never.
- I didn't know #2239 was such a big issue until the PR was made. if we ranked by impact, #2239 probably exceeded #2237 based on how prolonged unresolved windows CIs issues were across releases.

The main feeling this week has been excitement. There was lots of messaging and reading AI output, doing a lot of random configuring, and trying to follow the issue. Also feeling a lot of grandiose and mogging. Like woah so cool. Upstream candidate! beautiful #2243 issue! kill shots! woo

The real test is whether I am still thinking about this repo next week or still reading random things on the codebase. Have a tendency to keep on jumping around projects. Current approach is to take it easy, keep it light, follow my interests, and not force it. Main goal is consistency and exploring.

I think the style of Simon Willison's [the perfect commit](https://simonwillison.net/2022/Oct/29/the-perfect-commit/) and [code proven to work](https://simonwillison.net/2025/Dec/18/code-proven-to-work/), and choosing high leverage, large scale, neglected, and tractable things to work on were heavily applied this week.

I also burned up a lot of tokens. I've been [switching heavily](https://github.com/sacchen/passagemath-workspace/commit/a70ce49ec160acde7320fb469d24cb7b5cae3f04#diff-b335630551682c19a781afebcf4d07bf978fb1f8ac04c6bf87428ed5106870f5) between codex desktop (very high limits), claude code cli (primary), and gemini cli (high context). recently added copilot to the mix. I always like shiny new tools and opencode seemed good, but it requires API credits I don't want to spend; sticking to existing claude, gemini, and copilot subscriptions instead.

quick observations and ranked:
- codex desktop: very happy with high limits, which made me feel better, but canceled subscription on Mar 2
- claude code cli: solid primary. consistently smarter and critiqued gemini a lot. maybe better reasoning and critique than codex? 
- codex cli: uses less ram than desktop. still high limits
- claude code desktop: solid. prefer cli version. asks less permissions than cli
- claude code web: can't do `gh` and didn't have my local chat history
- gemini cli: struggled with actually writing to files and was overconfident on some fixes

3:09am end. need to actually sleep. this was generally a pattern this week. I would just take a quick look at github at 12am and now it's so late