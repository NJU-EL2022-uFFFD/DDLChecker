import {createApp} from 'vue'
import {Button, Cell, CellGroup, Icon, Menu, MenuItem, Avatar, Popup, OverLay, Form, FormItem, TextArea} from "@nutui/nutui-taro";
import './app.scss'
import Taro from "@tarojs/taro";
import {request} from "./util/request";
import {ENV_ID} from "./config";


const App = createApp({
  created() {
    // 如果不存在则注册新用户
    const r = request({
      path: "/user/register",
      method: "POST",
      data: {}
    })
    console.log(r)

    r.then((res) => {
      console.log(res)
      try {
        if (res.data.data.new) {
          Taro.showModal({
            title: '新用户注册',
            content: 'TODO: 新手指引',
            showCancel: false
          })
        }
      } catch (e) {
        console.error(e)
      }
    }).catch((reason) => {
      Taro.showModal({
        title: '网络错误',
        content: '连接到服务器时发生错误, 请稍后再试或反馈给我们: ' + JSON.stringify(reason),
        showCancel: false
      })
    })
  },
  onShow() {
  },
})

// 微信云托管初始化
Taro.cloud.init({
  env: ENV_ID
})


App.use(Button)
  .use(Cell)
  .use(CellGroup)
  .use(Icon)
  .use(Menu)
  .use(MenuItem)
  .use(Avatar)
  .use(Popup)
  .use(OverLay)
  .use(FormItem)
  .use(Form)
  .use(TextArea)

export default App
