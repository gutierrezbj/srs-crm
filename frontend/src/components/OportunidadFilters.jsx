import React from 'react';

const ESTADOS_LICITACION = [
    { value: 'all', label: 'Todos' },
    { value: 'nueva', label: 'Nueva' },
    { value: 'revisada', label: 'Revisada' },
    { value: 'en_preparacion', label: 'En preparación' },
    { value: 'enviada', label: 'Enviada' },
    { value: 'adjudicada', label: 'Adjudicada' },
    { value: 'no_adjudicada', label: 'No adjudicada' },
    { value: 'descartada', label: 'Descartada' }
];

const ESTADOS_ADJUDICACION = [
    { value: 'all', label: 'Todos' },
    { value: 'nueva', label: 'Nueva' },
    { value: 'revisada', label: 'Revisada' },
    { value: 'contactando', label: 'Contactando' },
    { value: 'convertida', label: 'Convertida' },
    { value: 'descartada', label: 'Descartada' }
];

const NIVELES = [
    { value: 'all', label: 'Todos' },
    { value: 'oro', label: '🥇 Oro' },
    { value: 'plata', label: '🥈 Plata' },
    { value: 'bronce', label: '🥉 Bronce' }
];

const OportunidadFilters = ({ filtros, onChange, tipo = 'licitacion', showPropietario = true }) => {
    const estados = tipo === 'licitacion' ? ESTADOS_LICITACION : ESTADOS_ADJUDICACION;

    const handleChange = (field, value) => {
        onChange({ [field]: value });
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {/* Búsqueda */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
                    <input
                        type="text"
                        value={filtros.q || ''}
                        onChange={(e) => handleChange('q', e.target.value)}
                        placeholder="Título, órgano..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>

                {/* Estado */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                    <select
                        value={filtros.estado || 'all'}
                        onChange={(e) => handleChange('estado', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                        {estados.map(e => (
                            <option key={e.value} value={e.value}>{e.label}</option>
                        ))}
                    </select>
                </div>

                {/* Nivel */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nivel</label>
                    <select
                        value={filtros.nivel || 'all'}
                        onChange={(e) => handleChange('nivel', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                        {NIVELES.map(n => (
                            <option key={n.value} value={n.value}>{n.label}</option>
                        ))}
                    </select>
                </div>

                {/* Propietario */}
                {showPropietario && (
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Asignado</label>
                        <select
                            value={filtros.propietario || 'all'}
                            onChange={(e) => handleChange('propietario', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="all">Todos</option>
                            <option value="me">Mis oportunidades</option>
                            <option value="null">Sin asignar</option>
                        </select>
                    </div>
                )}

                {/* Ordenar */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Ordenar por</label>
                    <select
                        value={`${filtros.sort}-${filtros.order}`}
                        onChange={(e) => {
                            const [sort, order] = e.target.value.split('-');
                            onChange({ sort, order });
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="scoring.total-desc">Score (mayor)</option>
                        <option value="scoring.total-asc">Score (menor)</option>
                        <option value="importe-desc">Importe (mayor)</option>
                        <option value="importe-asc">Importe (menor)</option>
                        <option value="dias_restantes-asc">Más urgentes</option>
                        <option value="creado_at-desc">Más recientes</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default OportunidadFilters;
