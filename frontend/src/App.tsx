import { ConfigProvider } from 'antd'
import viVN from 'antd/locale/vi_VN'
import PriceDashboard from './pages/PriceDashboard'

export default function App() {
  return (
    <ConfigProvider
      locale={viVN}
      theme={{
        token: {
          colorPrimary: '#0071e3',
          colorInfo: '#0071e3',
          borderRadius: 8,
          fontFamily: '"SF Pro Text", "SF Pro Icons", "Helvetica Neue", Helvetica, Arial, sans-serif',
          colorText: '#1d1d1f',
        },
        components: {
          Layout: {
            headerBg: 'rgba(0, 0, 0, 0.8)',
            bodyBg: '#000000',
          },
          Card: {
            borderRadiusLG: 8,
            colorBgContainer: '#f5f5f7',
          },
          Button: {
            borderRadius: 8,
            primaryShadow: 'none',
          },
        },
      }}
    >
      <PriceDashboard />
    </ConfigProvider>
  )
}
