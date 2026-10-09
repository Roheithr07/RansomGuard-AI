import React from 'react';
import { Outlet } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';

export const DashboardLayout: React.FC = () => {
  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
  );
};
