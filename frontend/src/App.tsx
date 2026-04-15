import { ConfigProvider } from 'antd'
import viVN from 'antd/locale/vi_VN'
import PriceDashboard from './pages/PriceDashboard'

export default function App() {
  return (
    <ConfigProvider locale={viVN}>
      <PriceDashboard />
    </ConfigProvider>
  )
}
