interface Project {
  banner: string; // 图片链接
  title: string; // 项目标题
  description: string; // 项目简介
  link: string; // 项目链接
  tag?: string; // 项目标签
}

/**
 * TODO: 缺项处理
 * 在此处填写你的项目介绍
 */
export const projectsInfo: Project[] = [
  {
    banner: "/project-img/dt.png",
    title: "dynamic-thread-pool",
    description:
      "集监控、告警、动态配置于一体的动态线程池",
    link: "https://github.com/cnzhangxy51/dynamic-thread-pool.git",
    tag: "Java",
  },
  {
    banner: "/project-img/raffle.png",
    title: "lucky-wheel",
    description:
        "基于DDD架构的抽奖系统",
    link: "https://lucky.xyfv.cn/?userId=fuming&activityId=100301",
    tag: "Java",
  },
];
