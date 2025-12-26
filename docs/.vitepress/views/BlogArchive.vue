<template>
  <div
    class="max-w-3xl px-4 pb-8 mx-auto my-20 sm:px-6 xl:max-w-5xl xl:px-0 dark:divide-slate-200/20"
  >
    <!-- 标题 -->
    <div class="relative flex justify-center mt-2 0">
      <h1 class="text-5xl font-bold">{{ hero.title || "Blogs" }}</h1>
      <span
        class="absolute text-6xl tracking-wider text-transparent -translate-x-1/2 opacity-60 bottom-1/3 left-1/2 bg-gradient-to-b from-black/20 to-black/10 bg-clip-text dark:from-white/20 dark:to-white/10"
        >{{ hero.title || "Blogs" }}</span
      >
    </div>

    <p class="mt-2 text-center text-black/50 dark:text-slate-500">{{ hero.subTitle }}</p>

    <!-- 主体 -->
    <ul class="grid grid-cols-1 pt-6 mt-6 lg:gap-8 lg:grid-cols-3">
      <!-- 所有文章 -->
<!--      <div-->
<!--        :class="categories ? 'col-span-2' : 'col-span-3'"-->
<!--        class="order-2 pt-6 lg:pt-0 lg:order-1 lg:mt-0"-->
<!--      >-->
<!--        <h1-->
<!--          class="pb-2 text-3xl font-bold transition-all duration-300 border-b-4 border-sky-500 dark:border-sky-700 w-fit hover:pr-6"-->
<!--        >-->
<!--          ✨ 近期更新-->
<!--        </h1>-->
<!--        <div class="mt-4" :class="flow ? 'columns-1 lg:columns-2 gap-8' : ''">-->
<!--          <PostCard-->
<!--            v-for="(post, index) of posts"-->
<!--            :key="post.date.time"-->
<!--            :post="post"-->
<!--            :flow="flow"-->
<!--          ></PostCard>-->
<!--        </div>-->
<!--      </div>-->

      <!-- 文章分类 -->
      <div v-if="categories || features" class="order-1 col-span-3 lg:order-2 ">
        <Sidebar :types="categories"></Sidebar>
      </div>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useData, useRoute } from "vitepress";
import Sidebar from "./BlogArchiveSidebar.vue";

const route = useRoute();
const { frontmatter: pageData, theme } = useData();
const { hero, types, features, flow } = pageData.value;

function resolveSidebarForPath(sidebar: any, p: string) {
  if (!sidebar || typeof sidebar !== "object") return undefined;
  // VitePress sidebar 常见形态：{ "/Notes/": {...}, "/foo/": {...} }，按“最长前缀匹配”
  const keys = Object.keys(sidebar).sort((a, b) => b.length - a.length);
  const key = keys.find((k) => p.startsWith(k));
  return key ? sidebar[key] : undefined;
}

const categories = computed(() => {
  if (types) return types;
  const sidebarData = resolveSidebarForPath(theme.value.sidebar, route.path);
  return sidebarData?.items?.map((item: any) => ({ name: item.text, link: item.link }));
});
</script>
