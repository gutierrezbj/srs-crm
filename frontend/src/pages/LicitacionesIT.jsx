import React from 'react';
import useOportunidades from '../hooks/useOportunidades';
import OportunidadesTable from '../components/OportunidadesTable';
import OportunidadFilters from '../components/OportunidadFilters';
import StatsCards from '../components/StatsCards';
import { useAuth } from '../context/AuthContext';

const LicitacionesIT = () => {
    const { user } = useAuth();
    const {
        oportunidades,
        stats,
        loading,
        error,
        pagination,
        filtros,
        setFiltros,
        changePage,
        updateEstado,
        asignar
    } = useOportunidades({ tipo: 'licitacion', sector: 'it' });

    return (
        <div className="p-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Licitaciones IT</h1>
                <p className="text-gray-600">Oportunidades de licitación del sector TI</p>
            </div>

            <StatsCards stats={stats} loading={loading} />

            <OportunidadFilters
                filtros={filtros}
                onChange={setFiltros}
                tipo="licitacion"
            />

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            <OportunidadesTable
                oportunidades={oportunidades}
                loading={loading}
                onUpdateEstado={updateEstado}
                onAsignar={asignar}
                tipo="licitacion"
                currentUserId={user?.user_id}
            />

            {pagination.pages > 1 && (
                <div className="mt-4 flex justify-between items-center">
                    <p className="text-sm text-gray-600">
                        Mostrando página {pagination.page} de {pagination.pages} ({pagination.total} total)
                    </p>
                    <div className="flex gap-2">
                        <button
                            onClick={() => changePage(pagination.page - 1)}
                            disabled={pagination.page <= 1}
                            className="px-3 py-1 border rounded disabled:opacity-50"
                        >
                            Anterior
                        </button>
                        <button
                            onClick={() => changePage(pagination.page + 1)}
                            disabled={pagination.page >= pagination.pages}
                            className="px-3 py-1 border rounded disabled:opacity-50"
                        >
                            Siguiente
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LicitacionesIT;
