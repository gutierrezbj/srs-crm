import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const useOportunidades = ({ tipo, sector, autoFetch = true }) => {
    const [oportunidades, setOportunidades] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [pagination, setPagination] = useState({
        total: 0,
        page: 1,
        pages: 1
    });

    const [filtros, setFiltros] = useState({
        estado: 'all',
        propietario: 'all',
        nivel: 'all',
        categoria: 'all',
        q: '',
        sort: 'scoring.total',
        order: 'desc',
        page: 1,
        limit: 50
    });

    const fetchOportunidades = useCallback(async (customFiltros = null) => {
        setLoading(true);
        setError(null);

        try {
            const params = new URLSearchParams();
            const f = customFiltros || filtros;

            if (tipo) params.append('tipo', tipo);
            if (sector && sector !== 'all') params.append('sector', sector);
            if (f.estado && f.estado !== 'all') params.append('estado', f.estado);
            if (f.propietario && f.propietario !== 'all') params.append('propietario', f.propietario);
            if (f.nivel && f.nivel !== 'all') params.append('nivel', f.nivel);
            if (f.categoria && f.categoria !== 'all') params.append('categoria', f.categoria);
            if (f.q) params.append('q', f.q);
            if (f.sort) params.append('sort', f.sort);
            if (f.order) params.append('order', f.order);
            if (f.page) params.append('page', f.page);
            if (f.limit) params.append('limit', f.limit);

            const response = await api.get(`/api/oportunidades?${params.toString()}`);

            setOportunidades(response.data.items || []);
            setPagination({
                total: response.data.total,
                page: response.data.page,
                pages: response.data.pages
            });

        } catch (err) {
            setError(err.response?.data?.detail || 'Error cargando oportunidades');
            setOportunidades([]);
        } finally {
            setLoading(false);
        }
    }, [tipo, sector, filtros]);

    const fetchStats = useCallback(async () => {
        try {
            const params = new URLSearchParams();
            if (tipo) params.append('tipo', tipo);
            if (sector && sector !== 'all') params.append('sector', sector);

            const response = await api.get(`/api/oportunidades/stats?${params.toString()}`);
            setStats(response.data);
        } catch (err) {
            console.error('Error cargando stats:', err);
        }
    }, [tipo, sector]);

    const updateEstado = async (expediente, nuevoEstado) => {
        try {
            await api.patch(`/api/oportunidades/${expediente}/estado`, { estado: nuevoEstado });
            await fetchOportunidades();
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'Error actualizando estado');
            return false;
        }
    };

    const asignar = async (expediente, propietario) => {
        try {
            await api.patch(`/api/oportunidades/${expediente}/asignar`, { propietario });
            await fetchOportunidades();
            return true;
        } catch (err) {
            setError(err.response?.data?.detail || 'Error asignando');
            return false;
        }
    };

    const updateFiltros = (newFiltros) => {
        setFiltros(prev => ({ ...prev, ...newFiltros, page: 1 }));
    };

    const changePage = (newPage) => {
        setFiltros(prev => ({ ...prev, page: newPage }));
    };

    useEffect(() => {
        if (autoFetch) {
            fetchOportunidades();
            fetchStats();
        }
    }, [filtros, autoFetch]);

    return {
        oportunidades,
        stats,
        loading,
        error,
        pagination,
        filtros,
        setFiltros: updateFiltros,
        changePage,
        refetch: fetchOportunidades,
        refetchStats: fetchStats,
        updateEstado,
        asignar
    };
};

export default useOportunidades;
