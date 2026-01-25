import React from 'react';

const formatImporte = (importe) => {
    if (!importe) return '0 €';
    if (importe >= 1000000) {
        return `${(importe / 1000000).toFixed(1)}M €`;
    }
    if (importe >= 1000) {
        return `${(importe / 1000).toFixed(0)}K €`;
    }
    return `${importe.toFixed(0)} €`;
};

const StatsCards = ({ stats, loading }) => {
    if (loading || !stats) {
        return (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className="bg-white rounded-lg shadow p-4 animate-pulse">
                        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                        <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                    </div>
                ))}
            </div>
        );
    }

    const cards = [
        { label: 'Total', value: stats.total, color: 'text-gray-900' },
        { label: 'Oro', value: stats.por_nivel?.oro || 0, color: 'text-yellow-600', icon: '🥇' },
        { label: 'Plata', value: stats.por_nivel?.plata || 0, color: 'text-gray-600', icon: '🥈' },
        { label: 'Bronce', value: stats.por_nivel?.bronce || 0, color: 'text-orange-600', icon: '🥉' },
        { label: 'Score Promedio', value: stats.score_promedio?.toFixed(0) || 0, color: 'text-blue-600' },
        { label: 'Importe Total', value: formatImporte(stats.importe_total), color: 'text-green-600' }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            {cards.map((card, i) => (
                <div key={i} className="bg-white rounded-lg shadow p-4">
                    <p className="text-sm text-gray-500">{card.label}</p>
                    <p className={`text-2xl font-bold ${card.color}`}>
                        {card.icon && <span className="mr-1">{card.icon}</span>}
                        {card.value}
                    </p>
                </div>
            ))}
            {stats.urgentes > 0 && (
                <div className="bg-red-50 rounded-lg shadow p-4 border border-red-200">
                    <p className="text-sm text-red-600">Urgentes</p>
                    <p className="text-2xl font-bold text-red-700">⚠️ {stats.urgentes}</p>
                </div>
            )}
        </div>
    );
};

export default StatsCards;
