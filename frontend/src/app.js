// import {createApp} from 'vue'
// import './app.scss'
//
// import 'taro-ui/dist/style/index.scss'
//
// const App = createApp({
//   onShow(options) {
//   },
//   // 入口组件不需要实现 render 方法，即使实现了也会被 taro 所覆盖
// })
//
// export default App

import {createApp} from 'vue'
import {createUI} from 'taro-ui-vue3'
// 引用全部组件样式
import 'taro-ui-vue3/dist/style/index.scss'

const App = createApp({
  onShow(options) {
  },
})

// 引用全部组件
const tuv3 = createUI()
App.use(tuv3)

export default App
