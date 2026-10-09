import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';

export const DashboardLayout: FC = () => {
  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
};
