import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Software Testing Handbook',
  tagline: 'TL;DR testing guides with diagrams and examples',
  favicon: 'img/favicon.ico',

  // Change `url` when you publish. For a GitHub Pages project site build with BASE_URL=/<repo>/
  url: 'https://boro741.github.io',
  baseUrl: process.env.BASE_URL ?? '/testing-handbook/',
  organizationName: 'boro741',
  projectName: 'testing-handbook',

  // Broken links fail the build (Definition of done, section 9 of HANDBOOK_PROMPT.md)
  onBrokenLinks: 'throw',
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'throw',
      onBrokenMarkdownImages: 'throw',
    },
  },
  themes: ['@docusaurus/theme-mermaid'],
  clientModules: ['./src/clientModules/d3-transition.ts'],

  i18n: {defaultLocale: 'en', locales: ['en']},

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'docs',
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          showLastUpdateTime: false,
        },
        blog: false,
        theme: {customCss: './src/css/custom.css'},
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        language: ['en'],
        docsRouteBasePath: '/',
        indexBlog: false,
        highlightSearchTermsOnTargetPage: true,
      },
    ],
  ],

  themeConfig: {
    colorMode: {respectPrefersColorScheme: true},
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
    navbar: {
      title: 'Testing Handbook',
      items: [
        {href: 'https://github.com/boro741/testing-handbook', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Built with Docusaurus. Sample data is labelled "Illustrative data".`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'java', 'yaml', 'hcl', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
