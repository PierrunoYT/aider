---
title: Patch in your browser
highlight_image: /assets/browser.jpg
parent: Usage
nav_order: 800
description: Patch can run in your browser, not just on the command line.
---
{% if page.date %}
<p class="post-date">{{ page.date | date: "%B %d, %Y" }}</p>
{% endif %}

# Patch in your browser

<div class="video-container">
  <video controls loop poster="/assets/browser.jpg">
    <source src="/assets/patch-browser-social.mp4" type="video/mp4">
    <a href="/assets/patch-browser-social.mp4">Patch browser UI demo video</a>
  </video>
</div>

<style>
.video-container {
  position: relative;
  padding-bottom: 101.89%; /* 1080 / 1060 = 1.0189 */
  height: 0;
  overflow: hidden;
}

.video-container video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>

Use patch's new experimental browser UI to collaborate with LLMs
to edit code in your local git repo.
Patch will directly edit the code in your local source files,
and [git commit the changes](https://aider.chat/docs/git.html)
with sensible commit messages.
You can start a new project or work with an existing git repo.
Patch works well with 
GPT-4o, Sonnet 3.7, and DeepSeek Chat V3 & R1.
It also supports [connecting to almost any LLM](https://aider.chat/docs/llms.html).

Use the `--browser` switch to launch the browser version of patch:

```
python -m pip install -U patch-code

export OPENAI_API_KEY=<key> # Mac/Linux
setx   OPENAI_API_KEY <key> # Windows, restart shell after setx

patch --browser
```
